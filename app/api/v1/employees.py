import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, delete, desc, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from app.core.security import check_permissions, get_current_user
from app.db.models.employee import Employee
from app.db.base import get_db
from app.schemas.employee import (
    EmployeeCreateRequest,
    EmployeeReadRequest,
    EmployeeUpdateRequest,
)
from app.db.models.department import Department
from app.db.models.rbac import User


router = APIRouter(prefix="/employees", tags=["Employees"])


db_dependency = Annotated[Session, Depends(get_db)]


@router.post(
    "/",
    response_model=EmployeeReadRequest,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_employee(db: db_dependency, employee_request: EmployeeCreateRequest):
    """
    Create a new employee in the database.

    Args:

        employee_request (EmployeeCreateRequest): The request body containing the details of the employee to create.
        - employee_number (str): The employee number.
        - first_name (str): The first name of the employee.
        - middle_name (str, optional): The middle name of the employee.
        - last_name (str): The last name of the employee.
        - department_id (int): The ID of the department the employee belongs to.

    Returns:

        Employee: The newly created employee model.

    Raises:

        HTTPException: If an integrity error or any other database error occurs.
    """
    try:
        # Verify if the department_id exists in the database
        stmt = select(Department).where(
            Department.department_id == employee_request.department_id
        )
        department_model = db.execute(stmt).scalars().first()
        if department_model is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with id {employee_request.department_id} not found.",
            )

        employee_model = Employee(
            employee_number=employee_request.employee_number,
            first_name=employee_request.first_name,
            middle_name=employee_request.middle_name,
            last_name=employee_request.last_name,
            department_id=employee_request.department_id,
        )

        db.add(
            employee_model
        )  # create a new instance of a model that is not yet added to the session

        db.commit()
        db.refresh(employee_model)  # Refresh the new instance

        return employee_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new employee.",
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
            detail="An error occurred while creating the new employee.",
        )


@router.get(
    "/",
    response_model=list[EmployeeReadRequest],
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_all_employees(
    db: db_dependency,
    limit: Optional[int] = Query(None, description="Number of records to return"),
    order_by: Optional[str] = Query(None, description="Order by column"),
    ascending: Optional[bool] = Query(True, description="Sort in ascending order"),
):
    """
    Fetches all employees from the database.
    Args:

        limit (int, optional): The number of records to return. Defaults to None.
        order_by (str, optional): The column to order the results by. Defaults to employee_id.
        ascending (bool, optional): Sort in ascending order. Defaults to True.
        Note: the allowed columns are "employee_id", "employee_number", "first_name", "middle_name", "last_name".
    Returns:

        list[Employee]: A list of Employee objects retrieved from the database.
    Raises:

        HTTPException: If an integrity error or any other database error occurs,
                       or if an unexpected error occurs during the operation.
    """

    try:
        allowed_columns = [
            "employee_id",
            "employee_number",
            "first_name",
            "middle_name",
            "last_name",
        ]  # Add valid column names here

        # Start building the query
        stmt = select(Employee)

        # Apply ordering
        # Validate and set the order_by column or a default value
        if order_by is None:
            order_by = "employee_id"
        order_by = (
            order_by.lower() if order_by.lower() in allowed_columns else "employee_id"
        )
        order_column = getattr(Employee, order_by)
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
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all employees.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all employees.",
        )


@router.get(
    "/id/{employee_id}",
    response_model=EmployeeReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_employee_by_id(db: db_dependency, employee_id: int = Path(gt=0)):
    """
    Fetch a employee record by its ID.
    Args:

        employee_id (int): The ID of the employee to fetch. Must be greater than 0.
    Returns:

        Employee: The employee model if found.
    Raises:

        HTTPException: If the employee is not found (404), if there is an integrity error (400),
                       or if there is a general database error (500) or if an unexpected error occurs during the operation (500).
    """

    try:
        stmt = select(Employee).where(Employee.employee_id == employee_id)
        employee_model = db.execute(stmt).scalars().first()

        if employee_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"employee with id {employee_id} not found.",
            )

        return employee_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the employee with id {employee_id}.",
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
            detail=f"An error occurred while fetching the employee with id {employee_id}.",
        )


@router.get(
    "/number/{employee_number}",
    response_model=EmployeeReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def read_employee_by_employee_number(
    db: db_dependency,
    employee_number: str = Path(..., min_length=1, max_length=8, regex=r"^\d+$"),
):
    """
    Fetch a employee record by its ID.
    Args:

        employee_number (str): The number of the employee to fetch. Must be a string of length 1-8 and contain only digits.
    Returns:

        Employee: The employee model if found.
    Raises:

        HTTPException: If the employee is not found (404), if there is an integrity error (400),
                       or if there is a general database error (500) or if an unexpected error occurs during the operation (500).
    """

    try:
        stmt = select(Employee).where(Employee.employee_number == employee_number)
        employee_model = db.execute(stmt).scalars().first()

        if employee_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"employee with number {employee_number} not found.",
            )

        return employee_model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the employee with number {employee_number}.",
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
            detail=f"An error occurred while fetching the employee with number {employee_number}.",
        )


@router.put(
    "/{employee_id}",
    response_model=EmployeeReadRequest,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def update_employee(
    db: db_dependency,
    employee_request: EmployeeUpdateRequest,
    employee_id: int = Path(gt=0),
):
    """
    Update an existing employee in the database.
    Args:

        employee_request (EmployeeUpdateRequest): The request body containing the details of the employee to update.
        - employee_number (str): The employee number.
        - first_name (str): The first name of the employee.
        - middle_name (str, optional): The middle name of the employee.
        - last_name (str): The last name of the employee.
        - department_id (int): The ID of the department the employee belongs to.
    Returns:

        Employee: The updated employee model.
    Raises:

        HTTPException: If the employee with the given ID is not found, or if there is an integrity error or other database error.
    """
    try:
        stmt = select(Employee).where(Employee.employee_id == employee_id)
        employee_model = db.execute(stmt).scalars().first()

        if employee_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"employee with id {employee_id} not found.",
            )

        # Loop through provided fields and update the corresponding fields in employee_model
        update_data = employee_request.model_dump(
            exclude_unset=True
        )  # Only get the provided fields

        for key, value in update_data.items():
            setattr(employee_model, key, value)  # Dynamically update the fields
        db.commit()
        db.refresh(employee_model)  # Refresh the updated instance
        return employee_model  # Return the updated model

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the employee with id {employee_id}.",
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
            detail=f"An error occurred while updating the employee with id {employee_id}.",
        )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_employee(db: db_dependency, employee_id: int = Path(gt=0)):
    """
    Delete a employee from the database.
    Args:

        employee_id (int): The ID of the employee to delete. Must be greater than 0.
    Raises:

        HTTPException: If the employee with the given ID is not found, or if there is an integrity error or other database error.
    Returns:

        None
    """

    try:
        stmt = select(Employee).where(Employee.employee_id == employee_id)
        employee_model = db.execute(stmt).scalars().first()
        if employee_model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"employee with id {employee_id} not found.",
            )

        stmt = delete(Employee).where(Employee.employee_id == employee_id)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the employee with id {employee_id}.",
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
            detail=f"An error occurred while deleting the employee with id {employee_id}.",
        )
