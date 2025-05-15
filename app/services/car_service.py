from app.repositories.car_repository import CarRepository

class NotFoundError(Exception):
    pass

class ServiceError(Exception):
    pass

class CarService:
    @staticmethod
    def list_cars(
            make: str = None,
            model: str = None,
            fuel: str = None,
            year: int = None,
            country: str = None,
            sort: str = None
    ) -> list:
        try:
            return CarRepository.get_filtered_cars(
                make=make,
                model=model,
                fuel_type=fuel,
                year=year,
                country=country,
                sort=sort
            )
        except Exception as e:
            raise ServiceError(f"Error fetching filtered cars: {e}")


    @staticmethod
    def get_car_details(car_id: int) -> dict:
        car = CarRepository.get_car_by_id(car_id)
        if not car:
            raise NotFoundError(f"Car with id {car_id} not found")
        return car

    @staticmethod
    def add_car(car_data: dict) -> bool:
        try:
            if not CarRepository.save_car(car_data):
                raise ServiceError("Car already exists")
            return True
        except Exception as e:
            raise ServiceError(f"Error adding car: {e}")

    @staticmethod
    def update_car(car_id: int, update_data: dict) -> bool:
        if not CarRepository.get_car_by_id(car_id):
            raise NotFoundError(f"Car with id {car_id} not found")
        try:
            if not CarRepository.update_car(car_id, update_data):
                raise ServiceError("Update failed")
            return True
        except Exception as e:
            raise ServiceError(f"Error updating car: {e}")

    @staticmethod
    def remove_car(car_id: int) -> bool:
        if not CarRepository.get_car_by_id(car_id):
            raise NotFoundError(f"Car with id {car_id} not found")
        try:
            if not CarRepository.delete_car(car_id):
                raise ServiceError("Deletion failed")
            return True
        except Exception as e:
            raise ServiceError(f"Error deleting car: {e}")

    @staticmethod
    def get_car(car_id: int) -> dict:
        return CarRepository.get_car_by_id(car_id)

    @staticmethod
    def get_cars_for_comparison(ids: list[int]) -> list[dict]:
        return CarRepository.get_cars_by_ids(ids)