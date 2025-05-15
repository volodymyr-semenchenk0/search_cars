from app.parsers.autoscout24_parser import AutoScout24Parser
from app.repositories.source_repository import SourceRepository
from app.services.car_service import NotFoundError


class SourceService:
    @staticmethod
    def list_sources() -> list[dict]:
        return SourceRepository.get_all()
    @staticmethod
    def get_source_by_id(id: int) -> dict:
        rec = SourceRepository.get_by_id(id)
        if not rec:
            raise NotFoundError(f"Source {id} not found")
        return rec