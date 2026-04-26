import torch
import torch.nn as nn
from torch.nn.attention.flex_attention import flex_attention

from .config import TrainingConfig


class AmbienceTransformer(nn.Module):
    """Minimal real-time transformer with FlexAttention telemetry for UE5 Niagara."""

    def __init__(self, config: TrainingConfig):
        super().__init__()
        self.config = config
        self.head_dim = config.d_model // config.n_heads

        self.embeddings = nn.Embedding(config.vocab_size, config.d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.n_heads,
            dim_feedforward=config.d_model * 4,
            dropout=0.1,
            activation="gelu",
            batch_first=True,
            norm_first=True,
            bias=True,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=config.n_layers,
            enable_nested_tensor=config.enable_nested_tensor,
        )

        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

    def forward(self, x: torch.Tensor, telemetry_buffer=None):
        def telemetry_mod(score, b, h, q_idx, kv_idx):
            if telemetry_buffer is not None:
                telemetry_buffer.write_telemetry(
                    loss=0.0, embeddings_norm=0.0, attention_max=score.max().item()
                )
            return score

        x = self.embeddings(x)

        # 4D reshape for FlexAttention
        batch, seq_len, _ = x.shape
        x = x.view(batch, seq_len, self.config.n_heads, self.head_dim)
        x = x.transpose(1, 2)

        # FlexAttention call
        attn_result = flex_attention(query=x, key=x, value=x, score_mod=telemetry_mod)

        # Handle tuple return
        attn_output = attn_result[0] if isinstance(attn_result, tuple) else attn_result

        # Reshape back
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch, seq_len, self.config.d_model)

        x = self.transformer(attn_output)
        logits = self.lm_head(x)
        return logits
