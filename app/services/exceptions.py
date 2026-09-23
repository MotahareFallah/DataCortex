class QuestionNotAnswerableError(Exception):
    """The question cannot be answered from the available data."""


class WriteRequestError(Exception):
    """The user asked for a data-modifying operation; the system is read-only."""
