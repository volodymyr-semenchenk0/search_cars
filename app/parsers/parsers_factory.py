from app.parsers.autoscout24_parser import AutoScout24Parser

PARSERS = {
    "AutoScout24": AutoScout24Parser,
}

class ParserFactory:
    @staticmethod
    def get(name: str, base_url: str, **filters):

        ParserCls = PARSERS.get(name)
        if not ParserCls:
            raise ValueError(f"Парсер для джерела «{name}» не реалізовано")

        return ParserCls(base_url=base_url, **filters)