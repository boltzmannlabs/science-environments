"""Bounded host configuration and public application actions."""
import hashlib,json
from typing import Annotated,Literal
from pydantic import Field,model_validator
from .schemas import Record,Identifier
from .portfolio_biocatalysis import BioSourceRecord
from .portfolio_condition_binding import RouteConditionBinding
from .portfolio_impurities import ImpurityAnnotation
from .portfolio_process import ProcessBasis
Application=Literal['inventory_planning','condition_optimization','impurity_analysis','process_route_selection','biocatalytic_synthesis']
SourceApplication=Literal['impurity_analysis','biocatalytic_synthesis']
STEP_APPLICATIONS={'condition_optimization','impurity_analysis','biocatalytic_synthesis'}


def plain(value):
    if hasattr(value,'model_dump'):value=value.model_dump(mode='json')
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    if len(raw.encode())>1_000_000:raise ValueError('Application payload exceeds one megabyte')
    return json.loads(raw)


def digest(value):return hashlib.sha256(json.dumps(plain(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class ApplicationConfig(Record):
    schema_version:Literal['srg-application-config-v1']='srg-application-config-v1'
    condition_binding:RouteConditionBinding|None=None
    impurity_annotations:Annotated[tuple[ImpurityAnnotation,...],Field(max_length=100)]=()
    biocatalytic_records:Annotated[tuple[BioSourceRecord,...],Field(max_length=100)]=()
    process_basis:ProcessBasis|None=None
    @model_validator(mode='after')
    def unique_sources(self):
        for ids in ([r.annotation_id for r in self.impurity_annotations],[r.record_id for r in self.biocatalytic_records]):
            if len(set(ids))!=len(ids):raise ValueError('Duplicate application source identifiers')
        return self


class ReportRequest(Record):
    application:Application
    route_ids:Annotated[tuple[Identifier,...],Field(min_length=1,max_length=3)]
    step_id:Identifier|None=None
    candidate_id:Identifier|None=None
    @model_validator(mode='after')
    def scope(self):
        if len(set(self.route_ids))!=len(self.route_ids):raise ValueError('Duplicate route IDs')
        if self.application in STEP_APPLICATIONS:
            if len(self.route_ids)!=1 or self.step_id is None:raise ValueError('Select exactly one stored route step')
        elif self.step_id is not None:raise ValueError('This report compares routes')
        if self.candidate_id is not None and self.application!='condition_optimization':raise ValueError('Candidate applies only to conditions')
        return self


class StepRequest(Record):
    route_id:Identifier
    step_id:Identifier


class ConditionOptionsRequest(StepRequest):
    offset:Annotated[int,Field(strict=True,ge=0,le=100000)]=0
    limit:Annotated[int,Field(strict=True,ge=1,le=20)]=20


class RouteObservationRequest(StepRequest):
    candidate_id:Identifier


class RouteImpurityRequest(StepRequest):
    top_k:Annotated[int,Field(strict=True,ge=1,le=10)]=5


class ApplicationSourcesRequest(ConditionOptionsRequest):
    application:SourceApplication


APPLICATION_INPUTS={'application_report':ReportRequest,'condition_options':ConditionOptionsRequest,
'observe_route_condition':RouteObservationRequest,'predict_route_impurities':RouteImpurityRequest,
'retrieve_application_sources':ApplicationSourcesRequest}


def tool_schemas():
    descriptions={'application_report':'Build a route-bound application report from stored inputs and recorded evidence; not experimental validation.',
    'condition_options':'Inspect registered condition alternatives and already observed measurements for a stored step.',
    'observe_route_condition':'Observe one registered condition alternative for a stored step within the shared replay budget.',
    'predict_route_impurities':'Run the configured impurity model on a stored step; hypotheses only, not measured concentrations.',
    'retrieve_application_sources':'Retrieve host-registered impurity or biocatalytic source records within the shared retrieval allowance.'}
    return [{'name':name,'description':descriptions[name],'parameters':model.model_json_schema()}for name,model in APPLICATION_INPUTS.items()]
