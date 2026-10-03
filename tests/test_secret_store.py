import pytest
import secret_store as ss

T = ss.Secret("selftest", "self-test key", "LV_SELFTEST_KEY")


@pytest.fixture
def memory(monkeypatch):
    @ss.register
    class Memory(ss.SecretBackend):
        name, writable, data = "memory", True, {}
        def get(self, s): return self.data.get(s.id)
        def set(self, s, v): self.data[s.id] = v
        def delete(self, s): return self.data.pop(s.id, None) is not None
        def where(self, s): return f"memory ({s.id})"
    monkeypatch.setenv("TEACHME_SECRET_BACKENDS", "env,memory")
    monkeypatch.delenv(T.env, raising=False)
    yield Memory
    ss.REGISTRY.pop("memory")


def test_store_get_delete_through_a_registered_backend(memory):
    assert ss.store_secret(T, "sk_" + "a" * 30) == "memory (selftest)"
    assert ss.get_secret(T) == ("sk_" + "a" * 30, "memory (selftest)")
    assert ss.delete_secret(T) == ["memory (selftest)"] and ss.get_secret(T) == (None, None)


def test_env_wins_over_stored(memory, monkeypatch):
    ss.store_secret(T, "sk_" + "a" * 30)
    monkeypatch.setenv(T.env, "sk_" + "e" * 30)
    assert ss.get_secret(T)[1] == f"env {T.env}"


@pytest.mark.parametrize("bad", ["", "short", 'sk_aaaaaaaaaaaaaaaaaaaaaa" -w x', "sk_ with spaces aaaaaaaaaaaaa"])
def test_values_that_could_break_a_command_are_rejected(memory, bad):
    with pytest.raises(ValueError):
        ss.store_secret(T, bad)


def test_unknown_backend_name(monkeypatch):
    monkeypatch.setenv("TEACHME_SECRET_BACKENDS", "vault")
    with pytest.raises(SystemExit, match="unknown secret backend"):
        ss.backends()


def test_mask_never_reveals_the_middle():
    assert ss.mask("sk_1234567890abcdef9z9z") == "sk_…9z9z"
