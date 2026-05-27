from sentence_transformers import SentenceTransformer

from app.config import settings


_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)

    return _model


def get_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(
        text,
        normalize_embeddings=True,
    ).tolist()
