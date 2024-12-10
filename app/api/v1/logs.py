import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, delete, desc, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from app.core.security import check_permissions, get_current_user
from app.db.base import get_db
from app.schemas.inventory_adjustment_log import (
    InventoryAdjustmentLogReadRequest,
)
from app.db.models.inventory_adjustment_log import InventoryAdjustmentLog


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get(
    "/inventory-adjustment-logs",
    # dependencies=[Depends(check_permissions("super user permission"))],
    response_model=list[InventoryAdjustmentLogReadRequest],
    status_code=status.HTTP_200_OK,
)
def read_all_inventory_adjustment_logs(
    db: db_dependency,
    limit: Optional[int] = Query(None, description="Number of records to return"),
    order_by: Optional[str] = Query(None, description="Order by column"),
    ascending: Optional[bool] = Query(True, description="Sort in ascending order"),
):
    """
    Fetch all inventory adjustment logs from the database.

    Args:

        limit (int, optional): The number of records to return. Defaults to None.
        order_by (str, optional): The column to order the results by. Defaults to log_id.
        ascending (bool, optional): Sort in ascending order. Defaults to True.
        Note: the allowed columns are "log_id".
    Returns:

        list[Department]: A list of Department objects.
    Raises:

        HTTPException: If an integrity error or any other database error occurs,
                       an HTTPException is raised with an appropriate status code
                       and error message.
    """

    try:
        allowed_columns = [
            "log_id",
        ]  # Add valid column names here

        # Start building the query
        stmt = select(InventoryAdjustmentLog)

        # Apply ordering
        # Validate and set the order_by column or a default value
        if order_by is None:
            order_by = "log_id"
        order_by = order_by.lower() if order_by.lower() in allowed_columns else "log_id"
        order_column = getattr(InventoryAdjustmentLog, order_by)
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
            detail="An error occurred while fetching all inventory adjustment logs.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all inventory adjustment logs.",
        )


@router.get(
    "/{log_id}",
    response_model=InventoryAdjustmentLogReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_inventory_adjustment_log(db: db_dependency, log_id: int = Path(gt=0)):
    """
    Fetch a inventory adjustment log by its ID from the database.
    Args:

        log_id (int): The ID of the inventory adjustment log to fetch. Must be greater than 0.
    Returns:

        Department: The inventory adjustment log object if found.
    Raises:

        HTTPException: If the inventory adjustment log is not found, or if there is an integrity error,
                       database error, or any other unexpected error.
    """

    try:
        stmt = select(InventoryAdjustmentLog).where(
            InventoryAdjustmentLog.log_id == log_id
        )
        log_model = db.execute(stmt).scalars().first()

        if log_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"inventory adjustment log with id {log_id} not found.",
            )

        return log_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the inventory adjustment log with id {log_id}.",
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
            detail=f"An error occurred while fetching the inventory adjustment log with id {log_id}.",
        )
