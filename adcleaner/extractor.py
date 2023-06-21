import re
import argparse
import jsonlines
from charset_mnbvc import api


class PPLCalculator:
    def __init__(self, model_id, device):
        from transformers import GPT2LMHeadModel, AutoTokenizer  # pylint: disable=import-outside-toplevel
        self.device = device
        self.model = GPT2LMHeadModel.from_pretrained(model_id).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    def calc(self, text):
        # reference: https://huggingface.co/docs/transformers/perplexity
        encodings = self.tokenizer(text, return_tensors="pt")
        max_length = self.model.config.n_positions
        stride = 512
        seq_len = encodings.input_ids.size(1)

        nlls = []
        prev_end_loc = 0
        for begin_loc in range(0, seq_len, stride):
            end_loc = min(begin_loc + max_length, seq_len)
            trg_len = (
                end_loc - prev_end_loc
            )  # may be different from stride on last loop
            input_ids = encodings.input_ids[:, begin_loc:end_loc].to(self.device)
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = self.model(input_ids, labels=target_ids)
                neg_log_likelihood = outputs.loss
            nlls.append(neg_log_likelihood)
            prev_end_loc = end_loc
            if end_loc == seq_len:
                break

        ppl = torch.exp(torch.stack(nlls).mean())  # pylint: disable=no-member
        return float(ppl)


class TextExtractor:
    def __init__(self, folder: str, keyword_file: str, outputfile: str, ppl: PPLCalculator, mode: int = 2):
        _, self.files_info = api.from_dir(folder, mode)
        self.folder = folder
        self.ptn = self._gen_ptn(keyword_file)
        self.ppl = ppl
        # for filter dulicated content, if too many content, may cause memory error!
        self.sets = set()
        self.outwriter = jsonlines.open(outputfile, mode="w")

    def __del__(self):
        try:
            self.outwriter.close()
        except Exception as e:
            print(e.args)

    def _gen_ptn(self, keyword_file):
        with open(keyword_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        ptns = r"|".join([line.strip() for line in lines if line.strip()])
        return re.compile(r".*(" + ptns + r").*")
        
    def record(self, ret):
        print(ret)
        self.outwriter.write(ret)

    def extract(self, file, enc):
        with open(file, "r", encoding=enc) as f:
            lines = f.readlines()
            striped_lines = []
            for raw_line in lines:
                lstriped = raw_line.strip()
                if lstriped:
                    striped_lines.append(lstriped)
            for idx, line in enumerate(striped_lines):
                if re.match(self.ptn, line):
                    if line in self.sets:
                        continue
                    self.sets.add(line)
                    ret = {
                        "file": file,
                        "line": idx,
                        "content": line,
                        "ppl": self.ppl.calc(line) if self.ppl else 0,
                    }
                    self.record(ret)

    def run(self):
        for file, enc in self.files_info:
            try:
                self.extract(file, enc)
            except Exception:
                pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-F", "--folder", type=str, required=True, help="目标文件夹")
    parser.add_argument("-K", "--keyword", type=str, required=True, help="关键词文件")
    parser.add_argument("-D", "--dest", type=str, required=True, help="输出文件")
    parser.add_argument("--ppl", action="store_true", help="是否计算ppl")
    parser.add_argument("--ppl-model", type=str, required=False, default="uer/gpt2-chinese-cluecorpussmall", help="计算ppl的模型")
    parser.add_argument("--ppl-device", type=str, required=False, default="cpu", help="计算ppl用的device, cpu or cuda")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    calc : PPLCalculator = None
    if args.ppl:
        import torch  # pylint: disable=import-outside-toplevel
        calc = PPLCalculator(args.ppl_model, args.ppl_device)
    et = TextExtractor(args.folder, args.keyword, args.dest, calc)
    et.run()
