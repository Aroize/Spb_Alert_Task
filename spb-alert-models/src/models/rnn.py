import torch
import torch.nn as nn
from torchsummaryX import summary


class AutoregressiveMultimodalRNN(nn.Module):

    def __init__(self, *args, **kwargs):
        super(AutoregressiveMultimodalRNN, self).__init__()
        self.lstm = nn.LSTM(kwargs['lstm_input'], kwargs['lstm_hidden'])
        max_seq = kwargs['lstm_hidden'] * kwargs['max_seq']
        self.kw, self.qw, self.vw = [
            nn.Linear(max_seq, max_seq)
            for _ in range(3)
        ]
        self.linears = [
            nn.Linear(max_seq, max_seq)
            for _ in range(kwargs["hidden"])
        ]
        self.out = nn.Sequential(
            nn.Linear(max_seq, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        hs = []
        hx = None
        for tensor in x:
            hx, out = self.lstm(tensor, hx)
            hs.append(out)
        k, v, q = self.kw(torch.tensor(hs)), self.vw(torch.tensor(hs)), self.qw(torch.tensor(hs))
        result = nn.functional.softmax(q * k.transpose()) * v
        for linear in self.linears:
            result = linear(result)
        return self.out(result)


