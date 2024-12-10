import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from app.db.base import get_db
from app.schemas.checkout_transaction import (
    CheckoutTransactionCreateRequest,
    CheckoutTransactionReadRequest,
)
from app.db.models.department import Department
from app.db.models.employee import Employee
from app.db.models.item import Item

from app.db.models.checkout_transaction import CheckoutTransaction
from app.db.models.checkout_item import CheckoutItem
from app.db.models.item_category import ItemCategory
from app.db.models.unit_of_measure import UnitOfMeasure
from app.db.models.inventory_adjustment_log import InventoryAdjustmentLog


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/transactions", tags=["Inventory Checkout"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def process_checkout(
    db: db_dependency, transaction_request: CheckoutTransactionCreateRequest
):
    """
    Processes a checkout transaction by validating the employee, department, and items,
    and then creating the transaction and associated checkout items in the database.
    Args:

        transaction_request (CheckoutTransactionCreateRequest): The request object containing
            the details of the checkout transaction, including employee_id, department_id,
            and a list of checkout items.
            # Example Transaction:
            # {
            #     "employee_id": 123,
            #     "department_id": 2,
            #     "checkout_items": [
            #         {
            #         "item_id": 456,
            #         "quantity": 2
            #         },
            #         {
            #         "item_id": 789,
            #         "quantity": 1
            #         }
            #     ]
            # }
    Raises:

        HTTPException:
        - If the employee, department, or any item is not found, or if an item
            does not have enough quantity in stock.
        - If there is an integrity error during the database transaction.
        - If there is a general database error during the transaction.
        - If there is an unexpected error during the transaction.
    Returns:

        dict: A dictionary containing a success message and the transaction details, including
            the transaction ID and creation timestamp.
    """

    # Example Transaction:
    # {
    #     "employee_id": 123,
    #     "department_id": 2,
    #     "checkout_items": [
    #         {
    #         "item_id": 456,
    #         "quantity": 2
    #         },
    #         {
    #         "item_id": 789,
    #         "quantity": 1
    #         }
    #     ]
    # }
    try:
        # Check if the employee and department exist
        models_to_check = [
            (
                Employee,
                Employee.employee_id,
                transaction_request.employee_id,
                "employee",
            ),
            (
                Department,
                Department.department_id,
                transaction_request.department_id,
                "department",
            ),
        ]

        for model, field, value, name in models_to_check:
            stmt = select(model).where(field == value)
            result = db.execute(stmt).scalars().first()
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{name.capitalize()} with id {value} not found.",
                )

        # Validate the list of checkout items
        for item in transaction_request.checkout_items:
            stmt = select(
                Item.item_id,
                Item.name,
                Item.category,
                Item.unit_of_measure,
                Item.quantity,
            ).where(Item.item_id == item.item_id)
            result = db.execute(stmt).fetchone()
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item with id {item.item_id} not found.",
                )

            # Check if the item has enough quantity
            if result.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item {result.name} has only {result.quantity} in stock.",
                )

            # Retrieve the category and unit of measure for the item
            stmt = select(ItemCategory.category_id).where(
                ItemCategory.category_id == result.category
            )
            category = db.execute(stmt).scalars().first()

            stmt = select(UnitOfMeasure.uom_id).where(
                UnitOfMeasure.uom_id == result.unit_of_measure
            )
            uom = db.execute(stmt).scalars().first()
            print(item.item_id, category, uom)
            # # Add retrieved category and unit of measure to the item
            # item.category_id = category
            # item.unit_of_measure = uom
            print("Item after adding category and uom ", item)

        # Create the checkout transaction
        new_transaction = CheckoutTransaction(
            employee_id=transaction_request.employee_id,
            department_id=transaction_request.department_id,
            total_items=len(transaction_request.checkout_items),
        )
        db.add(new_transaction)
        db.flush()  # Writes to the database to generate `transaction_id` but doesn't commit
        print("new_transaction.transaction_id ", new_transaction.transaction_id)
        # Create the checkout items
        for index, item in enumerate(transaction_request.checkout_items):
            print("CheckoutItem ", item)
            checkout_item = CheckoutItem(
                transaction_id=new_transaction.transaction_id,
                line_number=index + 1,
                item_id=item.item_id,
                quantity=item.quantity,
                category_id=category,
                unit_of_measure=uom,
            )
            db.add(checkout_item)

        db.commit()  # Commit the transaction and all lines
        print("Did go here!!!!")
        # The transaction is committed, so we can now fetch the transaction and checkout items
        stmt = select(CheckoutTransaction).where(
            CheckoutTransaction.transaction_id == new_transaction.transaction_id
        )
        checkout_transaction_result = db.execute(stmt).scalars().first()
        checkout_transaction_result_id = checkout_transaction_result.transaction_id
        print("checkout_transaction_result ", checkout_transaction_result_id)
        # After the transaction is committed, we need to update the quantity of the items accordingly
        if checkout_transaction_result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch the committed transaction.",
            )

        for item in checkout_transaction_result.checkout_items:
            stmt = select(Item).where(Item.item_id == item.item_id)
            result = db.execute(stmt).scalars().first()
            if result:
                old_value = result.quantity
                new_value = result.quantity - item.quantity
                result.quantity = new_value
                # log the inventory adjustment in the database
                inventory_adjustment_log = InventoryAdjustmentLog(
                    item_id=item.item_id,
                    old_quantity=old_value,
                    new_quantity=new_value,
                    quantity_changed=item.quantity,
                    adjustment_type="checkout",
                    scanned_invoice_item_id=None,
                    checkout_item_id=item.checkout_item_id,
                )
                db.add(inventory_adjustment_log)

        # commit the changes to the database
        db.commit()

        return {
            "message": "Checkout processed successfully",
            "transaction": checkout_transaction_result_id,
        }

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the checkout.",
        )
    except HTTPException as e:
        logging.error(f"HTTPException: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the checkout.",
        )


@router.get(
    "/",
    response_model=list[CheckoutTransactionReadRequest],
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_all_transactions(
    db: db_dependency,
    limit: Optional[int] = Query(None, description="Number of records to return"),
    order_by: Optional[str] = Query(None, description="Order by column"),
    ascending: Optional[bool] = Query(True, description="Sort in ascending order"),
):
    """
    Fetch all transactions from the database along with their associated permissions.

    Args:

        limit (int, optional): The number of records to return. Defaults to None.
        order_by (str, optional): The column to order the results by. Defaults to transaction_id.
        ascending (bool, optional): Sort in ascending order. Defaults to True.
        Note: the allowed columns are "transaction_id", "total_items", and "created_at".
    Returns:

        list[CheckoutTransaction]: A list of CheckoutTransaction objects with their associated items.
    Raises:

        HTTPException: If an integrity error or any other database error occurs,
                       an HTTPException is raised with an appropriate status code
                       and error message.
    """
    try:
        allowed_columns = [
            "transaction_id",
            "total_items",
            "created_at",
        ]  # Add valid column names here

        # Start building the query
        stmt = select(CheckoutTransaction)

        # Apply ordering
        # Validate and set the order_by column or a default value
        if order_by is None:
            order_by = "transaction_id"
        order_by = (
            order_by.lower()
            if order_by.lower() in allowed_columns
            else "transaction_id"
        )
        order_column = getattr(CheckoutTransaction, order_by)
        if order_column:
            if ascending:
                stmt = stmt.order_by(asc(order_column))
            else:
                stmt = stmt.order_by(desc(order_column))

        # Apply limit
        if limit is not None:
            stmt = stmt.limit(limit)

        # Execute the query
        return db.execute(stmt).scalars().all()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all transactions.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all transactions.",
        )


@router.get(
    "/{transaction_id}",
    response_model=CheckoutTransactionReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_transaction(db: db_dependency, transaction_id: int = Path(gt=0)):
    """
    Fetch a transaction by its ID from the database.
    Args:

        transaction_id (int): The ID of the transaction to fetch. Must be greater than 0.
    Returns:

        CheckoutTransaction: The transaction object if found.
    Raises:

        HTTPException: If the transaction is not found, or if there is an integrity error,
                       database error, or any other unexpected error.
    """

    try:
        stmt = select(CheckoutTransaction).where(
            CheckoutTransaction.transaction_id == transaction_id
        )
        transaction_model = db.execute(stmt).scalars().first()

        if transaction_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"transaction with id {transaction_id} not found.",
            )

        return transaction_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the transaction with id {transaction_id}.",
        )
    except HTTPException as e:
        logging.error(f"HTTPException: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the transaction with id {transaction_id}.",
        )
