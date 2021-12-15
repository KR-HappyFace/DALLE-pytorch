from pathlib import Path
from random import randint, choice

import PIL

from torch.utils.data import Dataset
from torchvision import transforms as T


class TextImageDataset(Dataset):
    def __init__(
        self,
        text_folder="/opt/ml/DALLE-Couture/data/caption",
        image_folder="/opt/ml/DALLE-Couture/data/cropped_img",
        text_len=128,
        image_size=256,
        truncate_captions=False,
        resize_ratio=0.75,
        tokenizer=None,
        shuffle=False,
    ):
        """
        @param folder: Folder containing images and text files matched by their paths' respective "stem"
        @param truncate_captions: Rather than throw an exception, captions which are too long will be truncated.
        """
        super().__init__()
        self.shuffle = shuffle
        #path = Path(folder)

        text_path = Path(text_folder)
        text_files = [*text_path.glob("**/*.txt")]

        image_path = Path(image_folder)
        image_files = [
            *image_path.glob("**/*.png"),
            *image_path.glob("**/*.jpg"),
            *image_path.glob("**/*.jpeg"),
        ]

        text_files = {text_file.stem: text_file for text_file in text_files}
        image_files = {image_file.stem: image_file for image_file in image_files}

        keys = image_files.keys() & text_files.keys()

        self.keys = list(keys)
        self.text_files = {k: v for k, v in text_files.items() if k in keys}
        self.image_files = {k: v for k, v in image_files.items() if k in keys}
        self.text_len = text_len
        self.truncate_captions = truncate_captions
        self.resize_ratio = resize_ratio
        self.tokenizer = tokenizer
        self.image_transform = T.Compose(
            [
                T.Lambda(lambda img: img.convert("RGB") if img.mode != "RGB" else img),
                # TODO: remove random resized crop while resolving RuntimeError: stack expects each tensor to be equal size, but got [3, 364, 237] at entry 0 and [3, 534, 535] at entry 1
                #T.RandomResizedCrop(image_size, scale=(self.resize_ratio, 1.0), ratio=(1.0, 1.0)),
                T.Resize((image_size, image_size)),
                T.ToTensor(),
            ]
        )

    def __len__(self):
        return len(self.keys)

    def random_sample(self):
        return self.__getitem__(randint(0, self.__len__() - 1))

    def sequential_sample(self, ind):
        if ind >= self.__len__() - 1:
            return self.__getitem__(0)
        return self.__getitem__(ind + 1)

    def skip_sample(self, ind):
        if self.shuffle:
            return self.random_sample()
        return self.sequential_sample(ind=ind)

    def __getitem__(self, ind):
        key = self.keys[ind]

        text_file = self.text_files[key]
        image_file = self.image_files[key]

        descriptions = text_file.read_text().split("\n")
        descriptions = list(filter(lambda t: len(t) > 0, descriptions))
        try:
            description = choice(descriptions)
        except IndexError as zero_captions_in_file_ex:
            print(f"An exception occurred trying to load file {text_file}.")
            print(f"Skipping index {ind}")
            return self.skip_sample(ind)

        tokenized_text = self.tokenizer.tokenize(
            description, self.text_len, truncate_text=self.truncate_captions
        ).squeeze(0)
        try:
            image_tensor = self.image_transform(PIL.Image.open(image_file))
        except (PIL.UnidentifiedImageError, OSError) as corrupt_image_exceptions:
            print(f"An exception occurred trying to load file {image_file}.")
            print(f"Skipping index {ind}")
            return self.skip_sample(ind)

        # Success
        return tokenized_text, image_tensor
