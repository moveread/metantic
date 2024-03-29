from pydantic import RootModel, BaseModel
from ._validate import validate
from ._str import str as stringify

PathT = RootModel[list[int|str]]

def Path(model: type[BaseModel]) -> type[PathT]:
    class PathT(RootModel):
        def __init__(self, path: list[int|str]):
            match validate(path, model.model_json_schema()):
                case None:
                    super().__init__(path)
                case ValueError() as err:
                    raise err
        def __str__(self) -> str:
            return stringify(self.root)
        
    return PathT