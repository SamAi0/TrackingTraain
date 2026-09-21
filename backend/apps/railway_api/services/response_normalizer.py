class ResponseNormalizer:
    @staticmethod
    def normalize(data, source="external_api", is_live=False, simulated=False, cached=False):
        import datetime
        return {
            "success": True,
            "data": data,
            "meta": {
                "source": source,
                "is_live": is_live,
                "simulated": simulated,
                "cached": cached,
                "fetched_at": datetime.datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def error(message, source="external_api", error_code="EXTERNAL_SERVICE_ERROR"):
        return {
            "success": False,
            "source": source,
            "error": message,
            "error_code": error_code
        }
