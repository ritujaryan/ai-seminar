from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def get(self, id: any) -> Optional[T]:
        raise NotImplementedError()
        
    def get_all(self) -> List[T]:
        raise NotImplementedError()
        
    def create(self, item: T) -> T:
        raise NotImplementedError()
        
    def update(self, id: any, item: T) -> T:
        raise NotImplementedError()
        
    def delete(self, id: any) -> bool:
        raise NotImplementedError()
