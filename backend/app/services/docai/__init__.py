"""Document AI Services."""
from .service import DocAIService, docai_service
from .parsers.invoice_parser import InvoiceParser, invoice_parser
from .parsers.contract_analyzer import ContractAnalyzer, contract_analyzer
from .parsers.resume_parser import ResumeParser, resume_parser
from .parsers.receipt_scanner import ReceiptScanner, receipt_scanner

__all__ = [
    "DocAIService",
    "docai_service",
    "InvoiceParser",
    "invoice_parser",
    "ContractAnalyzer",
    "contract_analyzer",
    "ResumeParser",
    "resume_parser",
    "ReceiptScanner",
    "receipt_scanner",
]
