import os
import datasets

from .AbsTask import AbsTask


class BeIRTask(AbsTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_data(self, eval_splits=None, **kwargs):
        """
        Load dataset from BeIR benchmark. TODO: replace with HF hub once datasets are moved there
        """
        try:
            from beir import util
        except ImportError:
            raise Exception("Retrieval tasks require beir package. Please install it with `pip install mteb[beir]`")

        USE_BEIR_DEVELOPMENT = False
        try:
            if self.description["beir_name"].startswith("cqadupstack"):
                raise ImportError("CQADupstack is incompatible with latest BEIR")
            from beir.datasets.data_loader_hf import HFDataLoader as BeirDataLoader

            USE_BEIR_DEVELOPMENT = True
        except ImportError:
            from beir.datasets.data_loader import GenericDataLoader as BeirDataLoader

        if self.data_loaded:
            return
        if eval_splits is None:
            eval_splits = self.description["eval_splits"]
        dataset = self.description["beir_name"]
        dataset, sub_dataset = dataset.split("/") if "cqadupstack" in dataset else (dataset, None)
        download_path = '/data/ashok-4983/instructor-embedding/evaluation/MTEB/data'
        self.corpus, self.queries, self.relevant_docs = {}, {}, {}
        for split in eval_splits:
            if USE_BEIR_DEVELOPMENT:
                hf_repo = f"BeIR/{dataset}"
                data_folder = ""
                if self.description.get("is_custom_dataset", False):
                    hf_repo = ""
                    data_folder = f"{download_path}/{dataset}"
                self.corpus[split], self.queries[split], self.relevant_docs[split] = BeirDataLoader(
                    hf_repo=hf_repo, data_folder=data_folder
                ).load(split=split)
            else:
                url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset}.zip"
                # download_path = os.path.join(datasets.config.HF_DATASETS_CACHE, "BeIR")
                # download_path = os.path.join('/gscratch/zlab/swj0419', "BeIR")
                data_path = util.download_and_unzip(url, download_path)
                data_path = f"{data_path}/{sub_dataset}" if sub_dataset else data_path
                self.corpus[split], self.queries[split], self.relevant_docs[split] = BeirDataLoader(
                    data_folder=data_path
                ).load(split=split)
        self.data_loaded = True
