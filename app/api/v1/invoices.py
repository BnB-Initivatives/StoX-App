import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from app.db.base import get_db
from app.schemas.scanned_invoice import (
    ScannedInvoiceReadRequest,
    ScannedInvoiceCreateRequest,
)
from app.db.models.employee import Employee
from app.db.models.item import Item

from app.db.models.scanned_invoice import ScannedInvoice
from app.db.models.scanned_invoice_item import ScannedInvoiceItem
from app.db.models.inventory_adjustment_log import InventoryAdjustmentLog
from app.db.models.vendor import Vendor


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/invoices", tags=["Scanning Invoices"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def process_scanned_invoice(
    db: db_dependency, scanned_invoice_request: ScannedInvoiceCreateRequest
):
    """
    Processes a checkout scanned invoice by validating the employee, department, and items,
    and then creating the scanned invoice and associated checkout items in the database.
    Args:

        scanned_invoice_request (ScannedInvoiceCreateRequest): The request object containing
            the details of the checkout scanned invoice, including invoice_number, scanned_by (employee_id),
            and a list of scanned items.
            # Example Scanned Invoice:
            # {
            #     "invoice_number": "INV123456",
            #     "vendor_name": "ABC Vendor",
            #     "scanned_by": 5, # e.g. employee_id of receiver = 5
            #     "image_file_path": "path/to/image/file.jpg", # Optional, the image of the scanned invoice should be uploaded by the frontend to a dedicated folder and just pass the path here
            #     "scanned_invoice_items": [
            #         {
            #         "item_code": "100012",
            #         "quantity": 2
            #         },
            #         {
            #         "item_code": "ABCD1234",
            #         "quantity": 1
            #         }
            #     ]
            # }
    Raises:

        HTTPException:
        - If the employee, or any item is not found in the database.
        - If there is an integrity error during the database scanned invoice.
        - If there is a general database error during the scanned invoice.
        - If there is an unexpected error during the scanned invoice.
    Returns:

        dict: A dictionary containing a success message and the scanned invoice details, including
            the scanned invoice ID and creation timestamp.
    """

    try:
        # Validate the employee exists
        stmt = select(Employee.employee_id).where(
            Employee.employee_id == scanned_invoice_request.scanned_by
        )
        employee_id = db.execute(stmt).scalars().first()
        if employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with id {scanned_invoice_request.scanned_by} not found.",
            )

        # Validate the vendor exists
        stmt = select(Vendor.vendor_id).where(
            Vendor.name == scanned_invoice_request.vendor_name
        )
        vendor_id = db.execute(stmt).scalars().first()
        if vendor_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vendor with name {scanned_invoice_request.vendor_name} not found.",
            )

        # Validate the image file path exists
        # if scanned_invoice_request.image_file_path:
        #     if not Path(scanned_invoice_request.image_file_path).exists():
        #         logging.error(f"The image file path provided does not exist.")
        #         raise HTTPException(
        #             status_code=status.HTTP_400_BAD_REQUEST,
        #             detail="The image file path provided does not exist.",
        #         )

        print("Scanned invoice request: ", scanned_invoice_request)
        # Validate the list of scanned items
        for item in scanned_invoice_request.scanned_invoice_items:
            stmt = select(Item.item_id, Item.item_code).where(
                Item.item_code == item.item_code
            )
            result = db.execute(stmt).fetchone()
            if result is None:
                logging.error(f"Item with item_code {item.item_code} not found.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Item with item_code {item.item_code} not found.",
                )
            print(item)
            print(result)
            # Add retrieved item_id to the item
            item.item_id = result.item_id
            print(item)

        # Create the checkout scanned invoice
        new_scanned_invoice = ScannedInvoice(
            invoice_number=scanned_invoice_request.invoice_number,
            vendor_id=vendor_id,
            scanned_by=scanned_invoice_request.scanned_by,
            image_file_path=scanned_invoice_request.image_file_path,
            total_items=len(scanned_invoice_request.scanned_invoice_items),
        )
        db.add(new_scanned_invoice)
        db.flush()  # Writes to the database to generate `scanned invoice_id` but doesn't commit

        # Create the checkout items
        for index, item in enumerate(scanned_invoice_request.scanned_invoice_items):
            checkout_item = ScannedInvoiceItem(
                scan_id=new_scanned_invoice.scan_id,
                line_number=index + 1,
                item_id=item.item_id,
                item_code=item.item_code,
                quantity=item.quantity,
            )
            db.add(checkout_item)

        db.commit()  # Commit the scanned invoice and all lines

        # The scanned invoice is committed, so we can now fetch the scanned invoice and checkout items
        stmt = select(ScannedInvoice).where(
            ScannedInvoice.scan_id == new_scanned_invoice.scan_id
        )
        scanned_invoice_result = db.execute(stmt).scalars().first()
        scanned_invoice_transaction_id = scanned_invoice_result.scan_id
        print("Final result: ", scanned_invoice_transaction_id)
        # After the scanned invoice is committed, we need to update the quantity of the items accordingly
        if scanned_invoice_result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch the committed transaction.",
            )

        for item in scanned_invoice_result.scanned_invoice_items:
            stmt = select(Item).where(Item.item_id == item.item_id)
            result = db.execute(stmt).scalars().first()
            if result:
                old_value = result.quantity
                new_value = result.quantity + item.quantity
                result.quantity = new_value
                # log the inventory adjustment in the database
                inventory_adjustment_log = InventoryAdjustmentLog(
                    item_id=item.item_id,
                    old_quantity=old_value,
                    new_quantity=new_value,
                    quantity_changed=item.quantity,
                    adjustment_type="received via scanned invoice",
                    scanned_invoice_item_id=item.scanned_invoice_item_id,
                    checkout_item_id=None,
                )
                db.add(inventory_adjustment_log)

        # commit the changes to the database
        db.commit()

        return {
            "message": "Scanned invoice processed successfully",
            "scanned invoice": scanned_invoice_transaction_id,
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
    response_model=list[ScannedInvoiceReadRequest],
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_all_scanned_invoices(
    db: db_dependency,
    limit: Optional[int] = Query(None, description="Number of records to return"),
    order_by: Optional[str] = Query(None, description="Order by column"),
    ascending: Optional[bool] = Query(True, description="Sort in ascending order"),
):
    """
    Fetch all scanned invoices from the database.

    Args:

        limit (int, optional): The number of records to return. Defaults to None.
        order_by (str, optional): The column to order the results by. Defaults to scan_id.
        ascending (bool, optional): Sort in ascending order. Defaults to True.
        Note: the allowed columns are "scan_id", "total_items", and "created_at".
    Returns:

        list[ScannedInvoice]: A list of ScannedInvoice objects with their associated items.
    Raises:

        HTTPException: If an integrity error or any other database error occurs,
                       an HTTPException is raised with an appropriate status code
                       and error message.
    """
    try:
        allowed_columns = [
            "scan_id",
            "total_items",
            "created_at",
        ]  # Add valid column names here

        # Start building the query
        stmt = select(ScannedInvoice)

        # Apply ordering
        # Validate and set the order_by column or a default value
        if order_by is None:
            order_by = "scan_id"
        order_by = (
            order_by.lower() if order_by.lower() in allowed_columns else "scan_id"
        )
        order_column = getattr(ScannedInvoice, order_by)
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
            detail="An error occurred while fetching all scanned invoices.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all scanned invoices.",
        )


@router.get(
    "/{scanned_invoice_id}",
    response_model=ScannedInvoiceReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_scanned_invoice(db: db_dependency, scanned_invoice_id: int = Path(gt=0)):
    """
    Fetch a scanned invoice by its ID from the database.
    Args:

        scanned invoice_id (int): The ID of the scanned invoice to fetch. Must be greater than 0.
    Returns:

        ScannedInvoice: The scanned invoice object if found.
    Raises:

        HTTPException: If the scanned invoice is not found, or if there is an integrity error,
                       database error, or any other unexpected error.
    """

    try:
        stmt = select(ScannedInvoice).where(
            ScannedInvoice.scan_id == scanned_invoice_id
        )
        scanned_invoice_model = db.execute(stmt).scalars().first()

        if scanned_invoice_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"scanned invoice with id {scanned_invoice_id} not found.",
            )

        return scanned_invoice_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the scanned invoice with id {scanned_invoice_id}.",
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
            detail=f"An error occurred while fetching the scanned invoice with id {scanned_invoice_id}.",
        )
