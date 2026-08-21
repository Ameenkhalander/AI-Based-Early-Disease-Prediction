"""Train a small skin-image CNN from a labeled ImageFolder dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms


class SkinCNN(nn.Module):
	def __init__(self, class_count: int) -> None:
		super().__init__()
		self.features = nn.Sequential(nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1)))
		self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.2), nn.Linear(128, class_count))

	def forward(self, images: torch.Tensor) -> torch.Tensor:
		return self.classifier(self.features(images))


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--data", type=Path, required=True)
	parser.add_argument("--output", type=Path, required=True)
	parser.add_argument("--epochs", type=int, default=8)
	parser.add_argument("--batch-size", type=int, default=32)
	args = parser.parse_args()
	if not args.data.exists():
		raise SystemExit(f"Dataset does not exist: {args.data}")
	if len([path for path in args.data.iterdir() if path.is_dir()]) < 2:
		raise SystemExit("Need at least two labeled class directories; no medical CNN was trained.")
	transform = transforms.Compose([transforms.Resize((224, 224)), transforms.RandomHorizontalFlip(), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
	dataset = datasets.ImageFolder(args.data, transform=transform)
	if len(dataset) < 10:
		raise SystemExit("Need at least 10 labeled images for a meaningful training run.")
	validation_size = max(1, int(len(dataset) * 0.2))
	training_set, validation_set = random_split(dataset, [len(dataset) - validation_size, validation_size], generator=torch.Generator().manual_seed(42))
	train_loader = DataLoader(training_set, batch_size=args.batch_size, shuffle=True, num_workers=0)
	validation_loader = DataLoader(validation_set, batch_size=args.batch_size, shuffle=False, num_workers=0)
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	model = SkinCNN(len(dataset.classes)).to(device)
	optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
	loss_function = nn.CrossEntropyLoss()
	for epoch in range(args.epochs):
		model.train()
		for images, labels in train_loader:
			images, labels = images.to(device), labels.to(device)
			optimizer.zero_grad(); loss_function(model(images), labels).backward(); optimizer.step()
		model.eval(); correct = total = 0
		with torch.no_grad():
			for images, labels in validation_loader:
				predictions = model(images.to(device)).argmax(dim=1).cpu(); correct += int((predictions == labels).sum()); total += len(labels)
		print(f"epoch={epoch + 1}/{args.epochs} validation_accuracy={correct / max(total, 1):.3f}")
	args.output.mkdir(parents=True, exist_ok=True)
	torch.jit.script(model.cpu().eval()).save(str(args.output / "model.pt"))
	(args.output / "metadata.json").write_text(json.dumps({"classes": dataset.classes, "input_size": 224, "architecture": "SkinCNN"}, indent=2), encoding="utf-8")
	print(f"Saved CNN artifact to {args.output}")


if __name__ == "__main__":
	main()
