import torch
import torch.nn as nn
from torch.nn.attention.flex_attention import flex_attention
from typing import Optional

from config import CausalLMConfig


class CausalLMModel(nn.Module):
    """Causal Language Model with rich attention telemetry for Niagara visualization."""

    def __init__(self, config: Optional[CausalLMConfig] = None):
        super().__init__()
        self.config = config or CausalLMConfig()
        self.head_dim = self.config.d_model // self.config.n_heads

        self.embeddings = nn.Embedding(self.config.vocab_size, self.config.d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.config.d_model,
            nhead=self.config.n_heads,
            dim_feedforward=self.config.d_model * self.config.feedforward_multiplier,
            dropout=self.config.dropout,
            activation=self.config.activation_function,
            batch_first=self.config.batch_first,
            norm_first=self.config.norm_first,
            bias=self.config.bias,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=self.config.n_layers
        )
        self.lm_head = nn.Linear(
            self.config.d_model, self.config.vocab_size, bias=False
        )

        # Temporary storage for rich attention stats during forward
        self._current_attention_stats = {}

    def forward(self, x: torch.Tensor, telemetry_buffer=None):
        """Forward pass with rich attention telemetry."""

        x = self.embeddings(x)

        batch, seq_len, _ = x.shape
        x = x.view(batch, seq_len, self.config.n_heads, self.head_dim)
        x = x.transpose(1, 2)

        # FlexAttention without score_mod (avoids graph break + unfused warning)
        attn_result = flex_attention(query=x, key=x, value=x)

        attn_output = attn_result[0] if isinstance(attn_result, tuple) else attn_result
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch, seq_len, self.config.d_model)

        x = self.transformer(attn_output)
        logits = self.lm_head(x)

        # === Rich Attention Telemetry (computed once per forward pass) ===
        if telemetry_buffer is not None:
            # For MVP we compute simple but useful stats from the attention output
            # (we can expand to full attention map later if needed)
            with torch.no_grad():
                # Global max attention
                global_max = attn_output.abs().max().item()
                # Mean attention magnitude
                mean_attention = attn_output.abs().mean().item()

            telemetry_buffer.write_telemetry(
                loss=0.0,
                embeddings_norm=self.embeddings.weight.norm().item(),
                attention_max=global_max,
                attention_mean=mean_attention,
                # Future: we can add per-head stats here as small tensors
            )

        return logits
