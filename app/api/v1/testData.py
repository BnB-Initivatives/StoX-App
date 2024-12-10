import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from app.core.security import check_permissions, get_current_user
from app.db.models.rbac import Permission, Role, RolePermission, User
from app.db.base import get_db
from app.schemas.permission import (
    PermissionCreateRequest,
    PermissionReadRequest,
)
from app.schemas.role import (
    RoleCreateRequest,
    RoleReadRequest,
)
from app.schemas.user import UserCreateRequest, UserReadRequest
from app.core.config import settings
from app.db.models.department import Department
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentReadRequest,
)
from app.db.models.vendor import Vendor
from app.schemas.vendor import VendorCreateRequest, VendorReadRequest
from app.db.models.item_category import ItemCategory
from app.schemas.item_category import ItemCategoryCreateRequest, ItemCategoryReadRequest
from app.db.models.unit_of_measure import UnitOfMeasure
from app.schemas.unit_of_measure import (
    UnitOfMeasureCreateRequest,
    UnitOfMeasureReadRequest,
)
from app.db.models.employee import Employee
from app.schemas.employee import EmployeeCreateRequest, EmployeeReadRequest
from app.db.models.item import Item
from app.schemas.item import ItemCreateRequest, ItemReadRequest

router = APIRouter(prefix="/insert-test-data", tags=["Test Data"])


db_dependency = Annotated[Session, Depends(get_db)]


@router.post(
    "/permissions",
    response_model=list[PermissionReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_permissions(
    db: db_dependency, permission_request: list[PermissionCreateRequest]
):
    """
    Create a list of permissions in the database.
    """
    try:
        for permission in permission_request:
            permission_model = Permission(
                name=permission.name,
                description=permission.description,
            )

            db.add(permission_model)

        db.commit()

        stmt = select(Permission).options(selectinload(Permission.roles))
        result = db.execute(stmt).scalars().all()

        return result

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_permissions(db: db_dependency):
    """
    Delete all permissions from the database.
    """

    try:
        stmt = delete(Permission)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/roles",
    response_model=list[RoleReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_roles(db: db_dependency, role_request: list[RoleCreateRequest]):
    """
    Create a list of roles in the database.
    """
    try:

        for role in role_request:
            role_model = Role(
                name=role.name,
                description=role.description,
            )

            db.add(role_model)

        db.commit()

        stmt = select(Role)
        roles = db.execute(stmt).scalars().all()

        return roles

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_roles(db: db_dependency):
    """
    Delete all roles from the database.
    """

    try:
        stmt = delete(Role)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.delete(
    "/roles-permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_roles_permissions(db: db_dependency):
    """
    Delete all roles and permissions associations from the database.
    """

    try:
        stmt = delete(RolePermission)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/users",
    response_model=list[UserReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_users(db: db_dependency, user_request: list[UserCreateRequest]):
    """
    Create a list of users in the database.
    """
    try:

        for user in user_request:
            user_model = User(
                user_name=user.user_name,
                hashed_password=settings.bcrypt_context.hash(user.password),
                employee_id=user.employee_id,
            )

            db.add(user_model)

        db.commit()

        stmt = select(User)
        roles = db.execute(stmt).scalars().all()

        return roles

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_users(db: db_dependency):
    """
    Delete all users from the database.
    """

    try:
        stmt = delete(User)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/departments",
    response_model=list[DepartmentReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_departments(
    db: db_dependency, department_request: list[DepartmentCreateRequest]
):
    """
    Create departments in the database.
    """
    try:

        for department in department_request:
            department_model = Department(
                name=department.name,
                description=department.description,
            )

            db.add(department_model)

        db.commit()

        stmt = select(Department)
        departments = db.execute(stmt).scalars().all()

        return departments

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/departments",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_departments(db: db_dependency):
    """
    Delete all departments from the database.
    """

    try:
        stmt = delete(Department)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/vendors",
    response_model=list[VendorReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_vendors(db: db_dependency, vendor_request: list[VendorCreateRequest]):
    """
    Create vendors in the database.
    """
    try:

        for vendor in vendor_request:
            vendor_model = Vendor(
                name=vendor.name,
                description=vendor.description,
            )

            db.add(vendor_model)

        db.commit()

        stmt = select(Vendor)
        vendors = db.execute(stmt).scalars().all()

        return vendors

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/vendors",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_vendors(db: db_dependency):
    """
    Delete all vendors from the database.
    """

    try:
        stmt = delete(Vendor)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/item-categories",
    response_model=list[ItemCategoryReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_item_categories(
    db: db_dependency, item_categories_request: list[ItemCategoryCreateRequest]
):
    """
    Create item categories in the database.
    """
    try:

        for category in item_categories_request:
            category_model = ItemCategory(
                name=category.name,
                description=category.description,
            )

            db.add(category_model)

        db.commit()

        stmt = select(ItemCategory)
        categories = db.execute(stmt).scalars().all()

        return categories

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/item-categories",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_item_categories(db: db_dependency):
    """
    Delete all item categories from the database.
    """

    try:
        stmt = delete(ItemCategory)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/uoms",
    response_model=list[UnitOfMeasureReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_uoms(db: db_dependency, uom_request: list[UnitOfMeasureCreateRequest]):
    """
    Create uoms in the database.
    """
    try:

        for uom in uom_request:
            uom_model = UnitOfMeasure(
                name=uom.name,
                abbreviation=uom.abbreviation,
                description=uom.description,
            )

            db.add(uom_model)

        db.commit()

        stmt = select(UnitOfMeasure)
        uoms = db.execute(stmt).scalars().all()

        return uoms

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/uoms",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_uoms(db: db_dependency):
    """
    Delete all uoms from the database.
    """

    try:
        stmt = delete(UnitOfMeasure)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/employees",
    response_model=list[EmployeeReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_employees(db: db_dependency, employee_request: list[EmployeeCreateRequest]):
    """
    Create employees in the database.
    """
    try:

        for emp in employee_request:
            emp_model = Employee(
                employee_number=emp.employee_number,
                first_name=emp.first_name,
                middle_name=emp.middle_name,
                last_name=emp.last_name,
                department_id=emp.department_id,
            )

            db.add(emp_model)

        db.commit()

        stmt = select(Employee)
        employees = db.execute(stmt).scalars().all()

        return employees

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/employees",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_employees(db: db_dependency):
    """
    Delete all employees from the database.
    """

    try:
        stmt = delete(Employee)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )


@router.post(
    "/items",
    response_model=list[ItemReadRequest],
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def create_items(db: db_dependency, item_request: list[ItemCreateRequest]):
    """
    Create items in the database.
    """
    try:

        for item in item_request:
            item_model = Item(
                item_code=item.item_code,
                name=item.name,
                description=item.description,
                category=item.category,
                vendor_id=item.vendor_id,
                owner_department=item.owner_department,
                has_barcode=item.has_barcode,
                barcode=item.barcode,
                image_path=item.image_path,
                unit_of_measure=item.unit_of_measure,
                quantity=item.quantity,
                low_stock_threshold=item.low_stock_threshold,
            )

            db.add(item_model)

        db.commit()

        stmt = select(Item)
        items = db.execute(stmt).scalars().all()

        return items

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the new permission.",
        )


@router.delete(
    "/items",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(check_permissions("super user permission"))],
)
def delete_items(db: db_dependency):
    """
    Delete all items from the database.
    """

    try:
        stmt = delete(Item)
        db.execute(stmt)
        db.commit()

    except IntegrityError as e:
        logging.error(f"Integrity error occurred: {str(e.orig)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting",
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
            detail=f"An error occurred while deleting",
        )
