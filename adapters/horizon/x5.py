from adapters.base import BasePlatformAdapter

class HorizonX5Adapter(BasePlatformAdapter):

    def get_platform_info(self) -> dict:
        return {
            "vendor": "Horizon",
            "platform": "X5",
        }

    def compile_model(
        self,
        model_path: str,
    ) -> dict:
        return {
            "status": "not_implemented",
            "platform": "X5",
            "model_path": model_path,
        }
    
    def deploy_model(
        self,
        model_path: str,
    ) -> dict:
        return {
            "status": "not_implemented",
            "platform": "X5",
            "model_path": model_path,
        }