from enum import Enum


class PlanningStrategy(Enum):
    # 路由器策略：用于在多个工具或路径之间进行选择的规划策略
    ROUTER = "router"
    # React 路由器策略：结合 React 思维链和路由选择的混合规划策略
    REACT_ROUTER = "react_router"
    # React 策略：基于 React 思维链的规划策略，通过推理和观察来执行任务
    REACT = "react"
    # 函数调用策略：直接调用可用函数来完成任务的规划策略
    FUNCTION_CALL = "function_call"
