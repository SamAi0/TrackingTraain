import logging
from django.db.models import Q
from .base_service import BaseRailwayService
from .response_normalizer import ResponseNormalizer
from ..exceptions import RailwayAPIException
from trains.models import Train

logger = logging.getLogger(__name__)

class TrainService(BaseRailwayService):
    @classmethod
    def search_train(cls, query):
        if not query:
            return ResponseNormalizer.error("Query parameter is required", error_code="INVALID_REQUEST")
            
        try:
            # Try External API First
            raw_data = cls.request("/api/v1/searchTrain", params={"search": query})
            
            # Normalize RapidAPI response
            trains = []
            if isinstance(raw_data, dict) and "data" in raw_data:
                results = raw_data.get("data", [])
                for tr in results:
                    trains.append({
                        "number": tr.get("trainNumber", ""),
                        "name": tr.get("trainName", ""),
                        "type": tr.get("trainType", "EXPRESS"),
                    })
            elif isinstance(raw_data, list):
                for tr in raw_data:
                    trains.append({
                        "number": tr.get("trainNumber", tr.get("number", "")),
                        "name": tr.get("trainName", tr.get("name", "")),
                        "type": tr.get("trainType", "EXPRESS"),
                    })
                    
            return ResponseNormalizer.normalize(trains, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API searchTrain failed: {e.message}. Falling back to DB.")
            return cls._fallback_search_train(query)
        except Exception as e:
            logger.error(f"Unexpected error in searchTrain: {str(e)}")
            return cls._fallback_search_train(query)
            
    @classmethod
    def _fallback_search_train(cls, query):
        """Fallback to existing local Train database"""
        trains = Train.objects.filter(
            Q(number__icontains=query) | 
            Q(name__icontains=query)
        )[:10]
        
        results = []
        for tr in trains:
            results.append({
                "number": tr.number,
                "name": tr.name,
                "type": tr.train_type
            })
            
        return ResponseNormalizer.normalize(
            results, 
            source="local_database", 
            simulated=False
        )

    @classmethod
    def trains_between(cls, from_station, to_station, date=None):
        if not from_station or not to_station:
            return ResponseNormalizer.error("from_station and to_station are required", error_code="INVALID_REQUEST")
            
        params = {
            "fromStationCode": from_station,
            "toStationCode": to_station,
        }
        if date:
            params["dateOfJourney"] = date
            
        try:
            # External API
            raw_data = cls.request("/api/v3/trainBetweenStations", params=params)
            
            trains = []
            results = raw_data.get("data", []) if isinstance(raw_data, dict) else raw_data
            
            for tr in results:
                trains.append({
                    "number": tr.get("trainNumber", ""),
                    "name": tr.get("trainName", ""),
                    "source": tr.get("fromStnCode", from_station),
                    "destination": tr.get("toStnCode", to_station),
                    "departure_time": tr.get("departureTime", ""),
                    "arrival_time": tr.get("arrivalTime", ""),
                    "duration": tr.get("duration", ""),
                    "classes": tr.get("availableClasses", []),
                    "type": tr.get("trainType", "EXPRESS")
                })
                
            return ResponseNormalizer.normalize(trains, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API trains_between failed: {e.message}. Falling back to DB.")
            return cls._fallback_trains_between(from_station, to_station)
        except Exception as e:
            logger.error(f"Unexpected error in trains_between: {str(e)}")
            return cls._fallback_trains_between(from_station, to_station)

    @classmethod
    def _fallback_trains_between(cls, from_station, to_station):
        # We will reuse the existing logic in TrackEase via Route model.
        # But this service should ideally query it. Let's do a basic join.
        from routes.models import RouteStation
        
        # Get routes that have both stations where from comes before to
        # A simpler approach: get all train numbers
        # Select train_id from routes_routestation where station_id = from 
        # INTERSECT 
        # Select train_id from routes_routestation where station_id = to
        # AND seq(from) < seq(to)
        
        # We will use Django ORM
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT t.number, t.name, r1.departure_time, r2.arrival_time, 
                           t.train_type
                    FROM trains_train t
                    JOIN routes_route rt ON rt.train_id = t.number
                    JOIN routes_routestation r1 ON r1.route_id = rt.id
                    JOIN routes_routestation r2 ON r2.route_id = rt.id
                    WHERE r1.station_id = %s 
                      AND r2.station_id = %s
                      AND r1.sequence_number < r2.sequence_number
                ''', [from_station, to_station])
                
                rows = cursor.fetchall()
                
            results = []
            for row in rows:
                results.append({
                    "number": row[0],
                    "name": row[1],
                    "source": from_station,
                    "destination": to_station,
                    "departure_time": str(row[2]) if row[2] else "",
                    "arrival_time": str(row[3]) if row[3] else "",
                    "duration": "",
                    "classes": [],
                    "type": row[4]
                })
                
            return ResponseNormalizer.normalize(
                results, 
                source="local_database", 
                simulated=False
            )
        except Exception as e:
            logger.error(f"Fallback trains_between error: {str(e)}")
            return ResponseNormalizer.error("Failed to fetch trains locally", source="local_database")

    @classmethod
    def get_classes(cls, train_number):
        if not train_number:
            return ResponseNormalizer.error("train_number is required", error_code="INVALID_REQUEST")
            
        try:
            raw_data = cls.request("/api/v1/getTrainClasses", params={"trainNo": train_number})
            
            data_dict = raw_data.get("data", {}) if isinstance(raw_data, dict) else {}
            classes = data_dict.get("classList", [])
            
            if not classes and isinstance(raw_data.get("data"), list):
                classes = raw_data.get("data")
                
            return ResponseNormalizer.normalize({
                "train_number": train_number,
                "classes": classes
            }, source="external_api")
            
        except RailwayAPIException as e:
            logger.warning(f"External API getTrainClasses failed: {e.message}. Falling back to DB.")
            return cls._fallback_classes(train_number)
        except Exception as e:
            logger.error(f"Unexpected error in getTrainClasses: {str(e)}")
            return cls._fallback_classes(train_number)

    @classmethod
    def _fallback_classes(cls, train_number):
        return ResponseNormalizer.normalize({
            "train_number": train_number,
            "classes": ["1A", "2A", "3A", "SL", "CC", "2S"]
        }, source="local_mock", simulated=True)
