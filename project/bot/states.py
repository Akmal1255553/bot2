from aiogram.fsm.state import State, StatesGroup


class GenerationStates(StatesGroup):
    choosing_style = State()
    choosing_aspect_ratio = State()
    waiting_for_image_prompt = State()
