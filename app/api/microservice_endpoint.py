from typing import Type, Dict, Tuple, Optional
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse

from app.config import server
from app.service.error_converter import convert_errors
from tracardi.process_engine.action.v1.connectors.trello.add_card_action.model.config import Config
from tracardi.process_engine.action.v1.connectors.trello.add_card_action.plugin import TrelloCardAdder, register
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent, Plugin, Spec, MetaData, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.service import plugin_context


class PluginExecContext(BaseModel):
    context: dict
    params: dict
    init: dict


class PluginConfig(BaseModel):
    name: str
    validator: Type[BaseModel]
    plugin: Type[ActionRunner]
    registry: Plugin


class ServiceConfig(BaseModel):
    name: str
    microservice: Plugin  # ? registry
    plugins: Dict[str, PluginConfig]


class ServicesRepo(BaseModel):
    repo: Dict[str, ServiceConfig]

    def get_all_services(self) -> Tuple[str, str]:
        for id, service in self.repo.items():
            yield id, service.name

    def get_all_action_plugins(self, service_id: str) -> Tuple[str, str]:
        if service_id in self.repo:
            service = self.repo[service_id]
            for id, plugin_config in service.plugins.items():
                yield id, plugin_config.name

    def get_plugin_microservice_plugin_registry(self, service_id: str) -> Optional[Plugin]:
        if service_id in self.repo:
            service = self.repo[service_id]
            return service.microservice
        return None

    def get_plugin(self, service_id: str, plugin_id: str) -> Optional[Type[ActionRunner]]:
        if service_id in self.repo:
            service = self.repo[service_id]
            if plugin_id in service.plugins:
                plugin_config = service.plugins[plugin_id]
                return plugin_config.plugin
        return None

    def get_plugin_registry(self, service_id: str) -> Optional[Plugin]:
        if service_id in self.repo:
            service = self.repo[service_id]
            return service.microservice
        return None

    def get_plugin_form_an_init(self, service_id: str, plugin_id: str) -> Tuple[Optional[dict], Optional[Form]]:
        if service_id in self.repo:
            service = self.repo[service_id]
            if plugin_id in service.plugins:
                plugin_config = service.plugins[plugin_id]
                return plugin_config.registry.spec.init, plugin_config.registry.spec.form
        return None, None

    def get_plugin_validator(self, service_id: str, plugin_id: str) -> Type[BaseModel]:
        if service_id in self.repo:
            service = self.repo[service_id]
            if plugin_id in service.plugins:
                plugin_config = service.plugins[plugin_id]
                return plugin_config.validator
        raise LookupError(f"Missing validator configuration for service {service_id} and plugin {plugin_id}")


repo = ServicesRepo(
    repo={
        "a307b281-2629-4c12-b6e3-df1ec9bca35a": ServiceConfig(
            name="Trello",
            microservice=Plugin(
                start=False,
                spec=Spec(
                    module='tracardi.process_engine.action.v1.microservice.plugin',
                    className='MicroserviceAction',
                    inputs=["payload"],
                    outputs=["payload", "error"],
                    version='0.7.2',
                    license="MIT",
                    author="Risto Kowaczewski",
                ),
                metadata=MetaData(
                    name='Trello Microservice',
                    desc='Microservice that runs Trello plugins.',
                    icon='trello',
                    group=["Connectors"],
                    remote=True,
                    documentation=Documentation(
                        inputs={
                            "payload": PortDoc(desc="This port takes payload object.")
                        },
                        outputs={
                            "payload": PortDoc(desc="This port returns microservice response.")
                        }
                    )
                )),
            plugins={
                "a04381af-c008-4328-ab61-0e73825903ce": PluginConfig(
                    name="Add card 1",
                    validator=Config,
                    plugin=TrelloCardAdder,
                    registry=register()
                )
            }
        )
    })

router = APIRouter()


@router.get("/services", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=dict)
async def get_all_services():
    services = list(repo.get_all_services())
    return {
        "total": len(services),
        "result": {id: name for id, name in services}
    }


@router.get("/actions", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=dict)
async def get_actions(service_id: str):
    actions = list(repo.get_all_action_plugins(service_id))
    return {
        "total": len(actions),
        "result": {id: name for id, name in actions}
    }


@router.get("/plugin/form", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=dict)
async def get_plugin(service_id: str, action_id: str):
    init, form = repo.get_plugin_form_an_init(service_id, action_id)

    return {
        "init": init if init is not None else {},
        "form": form.dict() if form is not None else None
    }


@router.get("/plugin/registry", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=Plugin)
async def get_plugin_registry(service_id: str):
    return repo.get_plugin_registry(service_id)


@router.post("/plugin/validate", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=dict)
async def validate_plugin_configuration(service_id: str, action_id: str, data: dict):
    try:
        validator = repo.get_plugin_validator(service_id, action_id)
        return validator(**data)
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(convert_errors(e))
        )


@router.post("/plugin/run", tags=["microservice"], include_in_schema=server.expose_gui_api, response_model=dict)
async def run_plugin(service_id: str, action_id: str, data: PluginExecContext):
    try:
        plugin_type = repo.get_plugin(service_id, action_id)
        print(data.init)
        if plugin_type:
            plugin = plugin_type()
            # set context
            data.context['node']['className'] = plugin_type.__name__
            data.context['node']['module'] = __name__
            plugin_context.set_context(plugin, data.context, include=['node'])
            print("context", data.context['node'])
            print("init", data.init)
            await plugin.set_up(data.init)
            print(await plugin.run(**data.params))
        return {}
    except ValidationError as e:
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(convert_errors(e))
        )
