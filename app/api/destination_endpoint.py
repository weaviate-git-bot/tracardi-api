from typing import Optional

from fastapi import APIRouter, Response, Depends

from tracardi.service.storage.driver.elastic import resource as resource_db
from tracardi.domain.destination import Destination
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination
from tracardi.service.storage.mysql.service.destination_service import DestinationService
from .auth.permissions import Permissions
from tracardi.config import tracardi
from ..service.grouping import group_mysql_records

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/destination", tags=["destination"], include_in_schema=tracardi.expose_gui_api)
async def save_destination(destination: Destination):
    """
    Upserts destination data.
    """

    ds = DestinationService()
    await ds.insert(destination)
    # record = DestinationRecord.encode(destination)
    # result = await destination_db.save(record)
    # await destination_db.refresh()
    # return result


@router.get("/destination/{id}", tags=["destination"], response_model=Optional[Destination],
            include_in_schema=tracardi.expose_gui_api)
async def get_destination(id: str, response: Response):
    """
    Returns destination or None if destination does not exist.
    """

    ds = DestinationService()
    record = await ds.load_by_id(id)

    if not record.exists():
        response.status_code = 404
        return None

    return record.map_to_object(map_to_destination)


@router.get("/destinations", tags=["destination"], response_model=dict,
            include_in_schema=tracardi.expose_gui_api)
async def get_destinations_list():
    """
    Returns destinations.
    """

    ds = DestinationService()
    records = await ds.load_all()

    if not records.exists():
        return {
            "total": 0,
            "result": []
        }

    result = list(records.map_to_objects(map_to_destination))

    return {
        "total": records.count(),
        "result": result
    }


    # storage_result = await destination_db.load_all()
    # return storage_result.dict()


@router.get("/destinations/type", tags=["destination"], response_model=dict, include_in_schema=tracardi.expose_gui_api)
async def get_destinations_type_list():
    """
    Returns destination types.
    """
    return {key: value for key, value in DestinationService.get_destination_types()}


@router.get("/destinations/by_tag", tags=["destination"], response_model=dict, include_in_schema=tracardi.expose_gui_api)
async def get_destinations_by_tag(query: str = None, start: int = 0, limit: int = 100) -> dict:
    ds = DestinationService()
    records = await ds.load_all()

    if not records.exists():
        return {
            "total": 0,
            "result": []
        }

    return group_mysql_records(
        records.map_to_objects(map_to_destination),
        query,
        group_by='tags',
        search_by='name'
    )


@router.delete("/destination/{id}", tags=["destination"], include_in_schema=tracardi.expose_gui_api)
async def delete_destination(id: str):
    """
    Deletes destination with given id
    """

    ds = DestinationService()
    await ds.delete_by_id(id)

    return True


@router.get("/destinations/entity",
            tags=["resource"],
            include_in_schema=tracardi.expose_gui_api)
async def list_destination_resources():
    data, total = await resource_db.load_destinations()
    result = {r.id: r for r in data if r.is_destination()}
    return result
