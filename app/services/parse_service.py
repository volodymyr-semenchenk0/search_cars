from app.parsers.parsers_factory import ParserFactory
from app.services.car_service import CarService
from app.services.source_service import SourceService


class ParseService:

    @staticmethod
    def parse_website(source_id: int, **filters) -> dict:
        src = SourceService.get_source_by_id(source_id)

        parser = ParserFactory.get(
            name=src['name'],
            base_url=src['url'],
            **filters
        ).parse()


