class ResponseNormalizer:
    @staticmethod
    def normalize(data, source="external_api", is_live=False, simulated=False, cached=False):
        import datetime
        
        # Mapping to required names
        if source == "external_api":
            mapped_source = "API"
        elif source in ["local_database", "local_mock", "merged"]:
            mapped_source = "DATASET_FALLBACK"
        else:
            mapped_source = source
            
        return {
            "success": True,
            "data": data,
            "data_source": mapped_source,
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
        if source == "external_api":
            mapped_source = "API"
        elif source in ["local_database", "local_mock"]:
            mapped_source = "DATASET_FALLBACK"
        else:
            mapped_source = source
            
        return {
            "success": False,
            "data_source": mapped_source,
            "error": message,
            "error_code": error_code
        }
