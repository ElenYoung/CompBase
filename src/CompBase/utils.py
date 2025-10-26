import re
from functools import wraps
from typing import Callable, Any, Dict, get_type_hints, get_args
from typing_extensions import Annotated
import inspect

def auto_validate(cls):
    """class decorator"""
    validate_methods = {'load_data_all', 'load_data_curr','get_daily_holdings','get_current_holdings'}
    
    for name in validate_methods:
        if hasattr(cls, name):
            method = getattr(cls, name)
            setattr(cls, name, validate_date_parameters(method))
    
    return cls

def validate_date_parameters(func: Callable) -> Callable:
    """Check the format of date in paramters."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        signature = inspect.signature(func)
        
        # mapping arg_name to arg_value
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        arg_values = bound_args.arguments
        
        # check all parameters
        for param_name, param_value in arg_values.items():
            # only check str
            if not isinstance(param_value, str):
                continue
                
            is_date_param = False
            
            if  "date" in param_name.lower():
                is_date_param = True
            
            if not is_date_param:
                continue
                
            # valid format
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", param_value):
                raise ValueError(
                    f"Invalid date format for parameter '{param_name}': '{param_value}'. "
                    "Expected format: YYYY-MM-DD"
                )
            
            try:
                year, month, day = map(int, param_value.split("-"))
                if not (1 <= month <= 12):
                    raise ValueError(f"Invalid month in {param_name}: {month}")
                if not (1 <= day <= 31):
                    raise ValueError(f"Invalid day in {param_name}: {day}")
                if month in [4, 6, 9, 11] and day > 30:
                    raise ValueError(f"Invalid day for month {month}: {day}")
                if month == 2:
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        max_day = 29
                    else:
                        max_day = 28
                    if day > max_day:
                        raise ValueError(f"Invalid day for February {year}: {day}")
            except ValueError as e:
                raise ValueError(f"Invalid date for parameter '{param_name}': {str(e)}")
        
        return func(*args, **kwargs)    
    return wrapper