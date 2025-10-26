from abc import ABC, abstractmethod, ABCMeta
from typing import Annotated, Dict, List, Tuple, Any, Callable
from utils import validate_date_parameters, auto_validate
import inspect

class SignatureMeta(ABCMeta):
    """元类：强制派生类方法签名与基类匹配"""
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        
        # 跳过基类检查
        if not bases:
            return
            
        # 获取基类
        for base in bases:
            if hasattr(base, '_abc_impl'):
                # 检查所有抽象方法
                for name, attr in base.__dict__.items():
                    if not getattr(attr, "__isabstractmethod__", False):
                        continue
                        
                    # 获取基类方法签名
                    base_sig = inspect.signature(attr)
                    
                    # 获取派生类方法
                    derived_method = getattr(cls, name, None)
                    if derived_method is None:
                        continue
                        
                    # 获取派生类方法签名
                    derived_sig = inspect.signature(derived_method)
                    
                    # 比较参数
                    base_params = list(base_sig.parameters.values())[1:]  # 跳过 self
                    derived_params = list(derived_sig.parameters.values())[1:]  # 跳过 self
                    
                    # 检查参数数量
                    if len(base_params) != len(derived_params):
                        raise TypeError(
                            f"Class {cls.__name__}: Method {name} has {len(derived_params)} parameters, "
                            f"but base class requires {len(base_params)}"
                        )
                    
                    # 检查参数名称
                    for i, (base_param, derived_param) in enumerate(zip(base_params, derived_params)):
                        if base_param.name != derived_param.name:
                            raise TypeError(
                                f"Class {cls.__name__}: Parameter {i+1} in {name} is named '{derived_param.name}', "
                                f"but base class requires '{base_param.name}'"
                            )


@auto_validate
class BaseResearcher(ABC, metaclass=SignatureMeta):

  _next_id = 0
  id_name_dict = {}

  def __init_subclass__(cls, **kwargs):
    if ('api_config' not in kwargs) or ('db_config' not in kwargs):
      raise TypeError(
        f"Derived Class {cls.__name__} must provide 'api_config' and 'db_config' as attribute"
          "(e.g. class MyResearcher(BaseResearcher, api_config=myapi_config, db_config=mydb_config):)"
      )
    
    api_config = kwargs.pop('api_config')
    if not isinstance(api_config, dict):
      raise TypeError(f"The api_config is expected to be of dict type")
    for key in ['model', 'api_key', 'base_url']:
      if key not in api_config.keys():
        raise ValueError(f"api_config dict must have 'model', 'api_key' and 'base_url'")
      
    db_config = kwargs.pop('db_config')
    if not isinstance(db_config, dict):
      raise TypeError(f"The db_config is expected to be of dict type")
    for key in ['host', 'port', 'user','password','database']:
      if key not in db_config.keys():
        raise ValueError(f"db_config dict must have 'host', 'port', 'user','password' and 'database'")
      
    super().__init_subclass__()

    cls.api_config = api_config
    cls.db_config = db_config
    cls.researcher_id = BaseResearcher._next_id
    BaseResearcher._next_id += 1

    researcher_name = kwargs.get('researcher_name', None)
    BaseResearcher.id_name_dict[cls.researcher_id] = researcher_name
    cls.name = researcher_name

  @abstractmethod
  def load_data_all(self,
                    start_date: Annotated[str, "start date in 'YYYY-MM-DD'"], 
                    end_date: Annotated[str, "end date in 'YYYY-MM-DD'"]) -> Any:
    """
    You need to load all the required data in this function and use quantchdb to access required data. 
    If other data is required, you can contact us.
    """
    pass

  @abstractmethod
  def load_data_curr(self,
                     curr_date: Annotated[str, "current date in 'YYYY-MM-DD'"]) -> Any:
    """
    You need to load the required data to get the curr_date holdings.
    """
    pass

  @abstractmethod
  def get_daily_holdings(self,
                         start_date: Annotated[str, "start date in 'YYYY-MM-DD'"], 
                         end_date: Annotated[str, "end date with in 'YYYY-MM-DD'"]) -> Dict[str, Dict[str, float]]:
    """
    You need to return the Dict of daily holdings, including stock code and corresponding weight. 
    The struct should be like:
    {'2025-01-01':{'000001': 0.5, 
                   '600519': 0.5},
     '2025-01-02':{'600519': 0.3, 
                   '300750':0.7}
    }
    The sum of weight should be no more than 1, that is you can hold cash to decrease your risk exposure.
    """
    pass

  @abstractmethod
  def get_current_holdings(self, 
                           curr_date: Annotated[str, "current date in 'YYYY-MM-DD'"]) -> Dict[str, Dict[str, float]]:
    """
    You need to return the holdings of curr_date.
    The struct should be like:
    {'2025-01-01':{'000001': 0.5, 
                   '600519': 0.5}
    }
    """
    pass



class BaseOptimizer(ABC):

  @abstractmethod
  def get_optimized_holdings(self, 
                             daily_holdings:Annotated[Any, "daily holdings of each researcher in DataFrame; columns are the researchers' id"],
                             start_date: Annotated[str, "start date in 'YYYY-MM-DD'"], 
                             end_date: Annotated[str, "end date with in 'YYYY-MM-DD'"]):
    pass


