from typing import Optional, Union
from pydantic import BaseModel
from datetime import date


class MAPPExtractResults(BaseModel):
    mrn: str
    date: Union[str, date]
    mdl_num: str
    assay: str
    cancer_type: Optional[str]
    primary_met: str
    nccn_category: str
    tumor_purity: Optional[str]
    tmb: Optional[str]
    msi: Optional[str]
    copy_number: Optional[list[str]]
    fusions: Optional[list[str]]
    somatic_muts: Optional[list[dict[str, str]]]
