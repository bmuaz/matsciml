import pytorch_lightning as pl
from torch.nn import LazyBatchNorm1d, SiLU

from ocpmodels.datasets.materials_project import MaterialsProjectDataset
from ocpmodels.lightning.data_utils import MaterialsProjectDataModule
from ocpmodels.models import GalaPotential
from ocpmodels.models.base import ScalarRegressionTask


model_args = {
    "D_in": 200,
    "hidden_dim": 128,
    "merge_fun": "concat",
    "join_fun": "concat",
    "invariant_mode": "full",
    "covariant_mode": "full",
    "include_normalized_products": True,
    "invar_value_normalization": "momentum",
    "eqvar_value_normalization": "momentum_layer",
    "value_normalization": "layer",
    "score_normalization": "layer",
    "block_normalization": "layer",
    "equivariant_attention": False,
    "tied_attention": True,
    "encoder_only": False,
}

mp_norms = {
    "formation_energy_per_atom_mean": -1.454,
    "formation_energy_per_atom_std": 1.206,
}

task = ScalarRegressionTask(
    mp_norms,
    encoder_class=GalaPotential,
    encoder_kwargs=model_args,
    output_kwargs={"norm": LazyBatchNorm1d, "hidden_dim": 256, "activation": SiLU},
    lr=1e-4,
    task_keys=["formation_energy_per_atom"],
)


dm = MaterialsProjectDataModule(
    dataset=MaterialsProjectDataset(
        "./mp_data/base/train/",
    ),
    val_split="./mp_data/base/val/",
    batch_size=12,
)

trainer = pl.Trainer(
    limit_train_batches=2,
    limit_val_batches=2,
    max_epochs=2,
    accelerator="cpu",
)
trainer.fit(task, datamodule=dm)
