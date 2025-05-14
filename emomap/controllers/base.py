import abc
from typing import Any, Dict, Type, TypeVar, Set, Optional

T = TypeVar('T')

class BaseController(abc.ABC):
    # Controllers might not always need a shared base __init__
    # if their dependencies vary significantly.
    pass

    @staticmethod
    def _convert_to_dict(obj: Any, memo: Optional[Set[int]] = None, depth: int = 0, max_depth: int = 3) -> Dict[str, Any]:
        """
        Safely converts a SQLAlchemy model instance to a dictionary,
        handling relationships appropriately with protection against circular references.
        
        Args:
            obj: The SQLAlchemy model instance to convert
            memo: Set of object ids already processed to prevent circular references
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent excessive nesting
            
        Returns:
            Dictionary representation of the model
        """
        if obj is None:
            return None
            
        # Initialize memo on first call
        if memo is None:
            memo = set()
            
        # Check for circular reference or max depth
        obj_id = id(obj)
        if obj_id in memo or depth > max_depth:
            # If we've seen this object before or reached max depth,
            # just return a simple identifier if possible
            if hasattr(obj, 'id'):
                return {"id": getattr(obj, 'id')}
            return {}
            
        # Add this object to memo
        memo.add(obj_id)
            
        # Check if it's a SQLAlchemy model by looking for __mapper__ attribute
        if hasattr(obj, '__mapper__'):
            # Handle SQLAlchemy model
            result = {}
            for key in obj.__mapper__.c.keys():
                result[key] = getattr(obj, key)
                
            # Handle relationships (if not at max depth)
            if depth < max_depth:
                for relationship in obj.__mapper__.relationships:
                    rel_key = relationship.key
                    try:
                        rel_obj = getattr(obj, rel_key)
                        if rel_obj is not None:
                            if hasattr(rel_obj, '__iter__') and not isinstance(rel_obj, str):
                                # It's a collection
                                result[rel_key] = [BaseController._convert_to_dict(item, memo, depth+1, max_depth) 
                                                  for item in rel_obj]
                            else:
                                # It's a single object
                                result[rel_key] = BaseController._convert_to_dict(rel_obj, memo, depth+1, max_depth)
                        else:
                            result[rel_key] = None
                    except Exception as e:
                        # If we encounter any error loading a relationship, skip it
                        result[rel_key] = None
                    
            return result
        
        # If it's not a SQLAlchemy model, return as is
        return obj
        
    @classmethod
    def _model_validate(cls, model_class: Type[T], obj: Any) -> T:
        """
        Safely validates a SQLAlchemy model into a Pydantic model.
        """
        if obj is None:
            return None
            
        # Convert SQLAlchemy model to dict with protection against circular references
        obj_dict = cls._convert_to_dict(obj)
        
        # Use Pydantic's model_validate with the dictionary
        return model_class.model_validate(obj_dict) 