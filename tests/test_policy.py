from agent.policy import evaluate, is_destructive_command


def test_readonly_allowed():
    decision = evaluate("docker_ps")
    assert decision.allowed is True
    assert decision.risk_tier == "read_only"


def test_destructive_blocked():
    decision = evaluate("shell_readonly", command="docker compose down")
    assert decision.allowed is False
    assert decision.risk_tier == "destructive"


def test_production_requires_ticket():
    decision = evaluate("deploy", command="deploy production")
    assert decision.allowed is False


def test_destructive_detection():
    assert is_destructive_command("rm -rf /tmp/example") is True
    assert is_destructive_command("ls -la") is False
