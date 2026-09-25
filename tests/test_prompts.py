from app.ai import prompts


def test_general_prompt_contains_question():
    messages = prompts.build_general_prompt("What is a thread?")
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "What is a thread?" in messages[1]["content"]


def test_rag_prompt_includes_context_chunks():
    messages = prompts.build_rag_prompt("Explain paging", ["Paging is ...", "Virtual memory is ..."])
    content = messages[1]["content"]
    assert "Paging is ..." in content
    assert "Virtual memory is ..." in content
    assert "Explain paging" in content


def test_rag_prompt_handles_no_context():
    messages = prompts.build_rag_prompt("Explain paging", [])
    assert "(no context found)" in messages[1]["content"]


def test_quiz_prompt_requests_correct_number_of_questions():
    messages = prompts.build_quiz_prompt(["some material"], num_questions=3)
    assert "3 multiple-choice" in messages[1]["content"]


def test_flashcards_prompt_uses_qa_format_instructions():
    messages = prompts.build_flashcards_prompt(["some material"], num_cards=4)
    assert "Q: <question>" in messages[1]["content"]
    assert "A: <answer>" in messages[1]["content"]
