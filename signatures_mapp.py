import dspy

from typing import Optional


class ExtractMRN(dspy.Signature):
    """
    Return the record associated with `MRN`.
    """
    ngs_report: str = dspy.InputField()
    mrn: str = dspy.OutputField()


class ExtractMDL(dspy.Signature):
    """
    Return the record associated with `MDL`. 
    
    For example, `MDL 24H-205D0085` --> 24H-205D0085.
    """
    ngs_report: str = dspy.InputField()
    mdl_num: str = dspy.OutputField()


class ExtractPurity(dspy.Signature):
    """
    Retrieve the tumor percentage under the section `Estimated tumor %:` if available.
    """
    ngs_report: str = dspy.InputField()
    tumor_purity: Optional[str] = dspy.OutputField()

class ExtractTMB(dspy.Signature):
    """
    Retrieve the tumor mutational burden (mutation per MB) under the section `TMB` if available.
    Examples:
    `CNVs  Fusions  TMB  MSI   APC  GATA3  GNAS  SMAD4  SUZ12  CDK4  FRS2  MDM2  PTPRB  None  3 mut/Mb  Stable (MSS)` --> '3 mut/MB'
    `SNVs/Indels  CNVs  Fusions     CBL  CDKN2C  ROR1  SF3B1  None  None` --> None
    """
    ngs_report: str = dspy.InputField()
    tmb: Optional[str] = dspy.OutputField()


class ExtractMSI(dspy.Signature):
    """
    Retrieve the DNA stability under the section `MSI` if available.
    Examples:
    `CNVs  Fusions  TMB  MSI   APC  GATA3  GNAS  SMAD4  SUZ12  CDK4  FRS2  MDM2  PTPRB  None  3 mut/Mb  Stable (MSS)` --> 'Stable (MSS)'
    `SNVs/Indels  CNVs  Fusions     CBL  CDKN2C  ROR1  SF3B1  None  None` --> None
    """
    ngs_report: str = dspy.InputField()
    msi: Optional[str] = dspy.OutputField()


class ExtractCNV(dspy.Signature):
    """
    Extract structured data from the section titled `Copy Number Variations (CNVs)     Gene Finding Genomic Position Cytoband` (and before `Gene Fusions`). Ignore all other sections.

    Extract the following fields:
    <GENE>: The gene name (e.g., CDK4, MDM2, EGFR, etc.)
    <FINDING>: The type of copy number variation (e.g., amplification, loss, etc.)
    <POSITION>: The genomic coordinates of the finding (e.g., chr17:37855802-37884307, chr12:69962810-69968735, etc.)
    <CYTOBAND>: The defined chromosome region of the finding (e.g., 12q14.1, 22q.1, 12q15, etc.)
    
    If no CNVs are identified, return None.
    """
    ngs_report: str = dspy.InputField()
    copy_number: Optional[list[str]] = dspy.OutputField()


class ExtractFusion(dspy.Signature):
    """
    Return all the values under the section `Gene Fusion Details`. If there are no fusions, return None.
    """
    ngs_report: str = dspy.InputField()
    fusions: Optional[list[str]] = dspy.OutputField()


# Extract the specified values below following the section of the report titled `Somatic Mutations (SNVs/Indels)     Gene DNA Protein Location VAF Type`. Ignore all other sections.
class ExtractSomatic(dspy.Signature):
    """
    Extract `Somatic Mutations (Gene DNA Protein Location VAF Type)` \ 'Soamtic variants (Gene Alteration Type Location VAF)`. Ignore all other sections.

    Extract the following fields:
    <GENE>: The gene name (e.g., TP53, RUNX1, etc.)
    <DNA_CHANGE>: The DNA change (e.g., c.3754C>A, c.86C>G, etc.)
    <PROTEIN_CHANGE>: The protein change (e.g., p.P1252T, p.I314T, etc.)
    <LOCATION>: the location of variant (e.g., Exon 1, Splice? (Exon 19), etc.)
    <VAF>: The Variant Allele Frequency (e.g., 6%, <5%, etc.; if there is `comment` for this field, return `See comment`)
    <VARIANT_TYPE>: The variant type (e.g., Missense, Nonsense, Frameshift, etc.)

    Do not leave any of the fields blank. Return the results as a list of Python dictionaries with the format:
    [
        {
            "Gene": "<GENE>",
            "DNA": "<DNA_CHANGE>",
            "Protein": "<PROTEIN_CHANGE>",
            "Location": <LOCATION>,
            "VAF": "<VAF>",
            "Type": "<VARIANT_TYPE>"
        },
        ...
    ]
    
    If no somatic mutations are identified, return None.
    """
    ngs_report: str = dspy.InputField()
    somatic_muts: Optional[list[dict[str, str]]] = dspy.OutputField()
     

class ExtractCancerType(dspy.Signature):
    """
    Return the value following the field `Cancer type:`

    For example: `Cancer Type: Lung Squamous Cell Carcinoma, Right Upper Lobe`
    cancer_type: Lung Squamous Cell Carcinoma, Right Upper Lobe
    """
    ngs_report: str = dspy.InputField()
    cancer_type: Optional[str] = dspy.OutputField()
     

class ClassifySource(dspy.Signature):
    """
    Classify the cancer type into only one of the following categories: 
        - Primary
        - Metastasis
        - Synchronous
        - Cannot be determined

    Examples:
    Lung Squamous Cell Carcinoma --> Primary
    Rectal Adenocarcinoma --> Primary
    Metastatic Adenocarcinoma --> Metastasis
    Adenocarcinoma --> Unknown
    Metastatic Carcinoma, Consistent with Breast Primary --> Metastasis
    """
    cancer_type: Optional[str] = dspy.InputField()
    source: str = dspy.OutputField()


class ClassifyCancerCategories(dspy.Signature):
    """
    Classify the cancer type into only one of the following categories: 
        - Ampullary Adenocarcinoma
        - Anal Cancer
        - Basal Cell Skin Cancer
        - Biliary Tract Cancers
        - Bladder Cancer
        - Bone Cancer
        - Breast Cancer   
        - Central Nervous System Cancers
        - Cervical Cancer
        - Colon Cancer
        - Dermatofibrosarcoma Protuberans
        - Esophageal and Esophagogastric Junction Cancers
        - Gastric Cancer
        - Gastrointestinal Stromal Tumors
        - Head and Neck Cancers
        - Hepatocellular Carcinoma
        - Kidney Cancer
        - Cutaneous Melanoma
        - Merkel Cell Carcinoma
        - Peritoneal Mesothelioma
        - Pleural Mesothelioma
        - Nephroblastoma (Wilms Tumor)
        - Neuroblastoma
        - Neuroendocrine and Adrenal Tumors
        - Non-Small Cell Lung Cancer
        - Occult Primary
        - Ovarian Cancer/Fallopian Tube Cancer/Primary Peritoneal Cancer
        - Pancreatic Adenocarcinoma
        - Pediatric Central Nervous System Cancers
        - Penile Cancer
        - Prostate Cancer
        - Rectal Cancer
        - Small Bowel Adenocarcinoma
        - Small Cell Lung Cancer
        - Soft Tissue Sarcoma
        - Squamous Cell Skin Cancer
        - Testicular Cancer
        - Thymomas and Thymic Carcinomas
        - Thyroid Carcinoma
        - Unspecified Neoplasm
        - Uterine Neoplasms
        - Vaginal Cancer
        - Vulvar Cancer

    Examples:
    Rectal Adenocarcinoma --> Rectal Cancer
    Sigmoid Adenocarcinoma --> Colon Cancer
    Appendiceal Adenocarcinoma --> Colon Cancer
    Lung Adenocarcinoma --> Non-Small Cell Lung Cancer
    Esophageal Adenocarcinoma --> Esophageal and Esophagogastric Junction Cancers
    """
    cancer_type: Optional[str] = dspy.InputField()
    cancer_category: str = dspy.OutputField()


class ExtractAll(dspy.Module):
    def __init__(self):
        super().__init__()
        self.mrn = dspy.Predict(ExtractMRN)
        self.mdl = dspy.Predict(ExtractMDL)
        self.ct = dspy.Predict(ExtractCancerType)
        self.met = dspy.Predict(ClassifySource)
        self.tp = dspy.Predict(ExtractPurity)
        self.sm = dspy.Predict(ExtractSomatic)
        self.tmb = dspy.Predict(ExtractTMB)
        self.msi = dspy.Predict(ExtractMSI)
        self.cnv = dspy.Predict(ExtractCNV)
        self.fusion = dspy.Predict(ExtractFusion)
        self.reclassify = dspy.ChainOfThought(ClassifyCancerCategories)

    def get_cancer_type(self, ngs_report: str) -> str:
        return self.ct(ngs_report=ngs_report).cancer_type
    
    def forward(self, ngs_report: str) -> dict:
        mrn = self.mrn(ngs_report=ngs_report).mrn
        mdl = self.mdl(ngs_report=ngs_report).mdl_num
        tp = self.tp(ngs_report=ngs_report).tumor_purity
        sm = self.sm(ngs_report=ngs_report).somatic_muts
        tmb = self.tmb(ngs_report=ngs_report).tmb
        msi = self.msi(ngs_report=ngs_report).msi
        cnv = self.cnv(ngs_report=ngs_report).copy_number
        fusion = self.fusion(ngs_report=ngs_report).fusions
        
        ct = self.get_cancer_type(ngs_report)
        met = self.met(cancer_type=ct).source
        cc = self.reclassify(cancer_type=ct).cancer_category

        return {
            'mrn': mrn,
            'mdl': mdl,
            'tp': tp,
            'sm': sm,
            'cnv': cnv,
            'fusion': fusion,
            'tmb': tmb,
            'msi': msi,
            'ct': ct,
            'met': met,
            'cc': cc
        }
