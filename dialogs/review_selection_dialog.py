# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice, FoundChoice
from botbuilder.core import MessageFactory


class ReviewSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(ReviewSelectionDialog, self).__init__(
            dialog_id or ReviewSelectionDialog.__name__
        )

        self.COMPANIES_SELECTED = "value-companiesSelected"
        self.DONE_OPTION = "结束对话"

        self.company_options = [
            "我的游戏转账掉单",
            "我的流水还差多少",
            "我的vip升级进度",
        ]

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [self.selection_step, self.loop_step]
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def selection_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # step_context.options will contains the value passed in begin_dialog or replace_dialog.
        # if this value wasn't provided then start with an emtpy selection list.  This list will
        # eventually be returned to the parent via end_dialog.
        selected: [
            str
        ] = step_context.options if step_context.options is not None else []
        step_context.values[self.COMPANIES_SELECTED] = selected

        if len(selected) == 0:
            message = (
                f"请选择您要咨询的问题或者`{self.DONE_OPTION}`"
            )
        elif "我的游戏转账掉单" in selected:
            message = (
                f"请您提供您的单号，小v这为您查询。"
            )
            selected.remove("我的游戏转账掉单")
        elif "我的流水还差多少" in selected:
            message = (
                f"您的未完成投注额是XXXX"
            )
            selected.remove("我的流水还差多少")
        elif "我的vip升级进度" in selected:
            message = (
                f"您的存款还差XXXX，投注额还差XXXX，就可以升级呢"
            )
            selected.remove("我的vip升级进度")

        else:
            message = (
                f"You have selected **{selected[0]}**. You can review an additional company, "
                f"or choose `{self.DONE_OPTION}` to finish. "
            )

        # create a list of options to choose, with already selected items removed.
        options = self.company_options.copy()
        options.append(self.DONE_OPTION)
        options = [i for i in options if i not in selected]
        if len(selected) > 0:
            # options.remove(selected[0])
            options=[i for i in options if i not in selected]

        # prompt with the list of choices
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message),
            retry_prompt=MessageFactory.text("您的订单XXXX，请您在刷新试试"),
            choices=self._to_choices(options),
        )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    def _to_choices(self, choices: [str]) -> List[Choice]:
        choice_list: List[Choice] = []
        for choice in choices:
            choice_list.append(Choice(value=choice))
        return choice_list

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        selected: List[str] = step_context.values[self.COMPANIES_SELECTED]
        choice: FoundChoice = step_context.result
        done = choice.value == self.DONE_OPTION

        # If they chose a company, add it to the list.
        if not done:
            selected.append(choice.value)

        # If they're done, exit and return their list.
        if done or len(selected) >= 10:
            return await step_context.end_dialog(selected)

        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(
            ReviewSelectionDialog.__name__, selected
        )
