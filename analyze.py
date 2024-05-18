import argparse
import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

DEFAULT_INPUT_FILE = "sample_input/sample_weightlifting_data.csv"
DEFAULT_OUTPUT_DIR = "sample_output"


class WeightliftingAnalyzer:

    def analyze(self, input_file: str, output_dir: str):
        logging.info(f"Analyzing {input_file}")
        self.input_file = input_file
        self.output_dir = output_dir
        self.graphs_dir = f"{output_dir}/graphs"
        os.makedirs(self.graphs_dir, exist_ok=True)

        df = self.read_data()
        self.avg_weight_per_exercise(df)
        self.avg_weight_per_lift_per_day(df)
        self.total_weight_per_day(df)
        self.create_pdf_from_images()

    def read_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.input_file)
        # Convert 'Date' column to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def avg_weight_per_exercise(self, df: pd.DataFrame):
        # Calculate average weight lifted per exercise per person over time
        avg_weight_per_exercise_time = (
            df.groupby(["Person", "Exercise Name", "Date"])["Weight"]
            .mean()
            .reset_index()
        )

        for person, data in avg_weight_per_exercise_time.groupby("Person"):
            plt.figure(figsize=(10, 6))
            for exercise, exercise_data in data.groupby("Exercise Name"):
                plt.plot(
                    exercise_data["Date"],
                    exercise_data["Weight"],
                    marker="o",
                    label=f"{exercise}",
                )

            plt.title(f"Average Weight Lifted per Exercise over Time - {person}")
            plt.xlabel("Date")
            plt.ylabel("Average Weight Lifted")
            plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
            plt.xticks(rotation=45)
            plt.tight_layout()
            img_file = f"{self.graphs_dir}/avg_weight_per_exercise_{person}.png"
            plt.savefig(img_file)
            logging.info(f"Created {img_file}")
            plt.close()

    def avg_weight_per_lift_per_day(self, df: pd.DataFrame):
        # Calculate average weight lifted per exercise per person per day
        avg_weight_per_exercise_day = (
            df.groupby(["Exercise Name", "Date", "Person"])["Weight"]
            .mean()
            .reset_index()
        )

        # Plot each exercise's data separately
        for exercise, data in avg_weight_per_exercise_day.groupby("Exercise Name"):
            plt.figure(figsize=(10, 6))
            for person, person_data in data.groupby("Person"):
                plt.plot(
                    person_data["Date"],
                    person_data["Weight"],
                    marker="o",
                    label=f"{person}",
                )

            plt.title(f"Average Weight Lifted per Day - {exercise}")
            plt.xlabel("Date")
            plt.ylabel("Average Weight Lifted")
            plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
            plt.xticks(rotation=45)
            plt.tight_layout()
            img_file = f"{self.graphs_dir}/avg_weight_per_person_{exercise}.png"
            plt.savefig(img_file)
            logging.info(f"Created {img_file}")
            plt.close()

    def total_weight_per_day(self, df: pd.DataFrame):
        # Calculate total weight lifted per person
        df["Total Weight"] = df["Weight"] * df["Reps"]

        plt.figure(figsize=(10, 6))
        for person, person_data in df.groupby("Person"):
            total_weight_per_day = person_data.groupby("Date")["Total Weight"].sum()
            plt.plot(
                total_weight_per_day.index,
                total_weight_per_day.values,
                marker="o",
                label=person,
            )

        plt.title("Total Weight Lifted Over Time for Each Person")
        plt.xlabel("Date")
        plt.ylabel("Total Weight Lifted")
        plt.xticks(rotation=45)
        plt.legend(title="Person")
        plt.tight_layout()
        img_file = f"{self.graphs_dir}/total_weight_lifted_per_person.png"
        plt.savefig(img_file)
        logging.info(f"Created {img_file}")
        plt.close()

    # Combine all PNG images into a single PDF
    def create_pdf_from_images(self):
        pdf_filename = f"{self.output_dir}/out.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)

        for filename in sorted(os.listdir(self.graphs_dir)):
            if not filename.endswith(".png"):
                continue

            filepath = os.path.join(self.graphs_dir, filename)
            img = ImageReader(filepath)
            width, height = img.getSize()
            aspect_ratio = width / height
            max_width = 600  # Adjust this value as needed

            if width > max_width:
                width = max_width
                height = width / aspect_ratio

            c.drawImage(
                img,
                (letter[0] - width) / 2,
                (letter[1] - height) / 2,
                width=width,
                height=height,
            )
            c.showPage()

        c.save()
        logging.info(f"Saved PDF to {pdf_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weightlifting Data Analyzer")
    parser.add_argument(
        "--input-file", type=str, default=DEFAULT_INPUT_FILE, help="Input CSV file path"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save output files",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    analyzer = WeightliftingAnalyzer()
    analyzer.analyze(args.input_file, args.output_dir)
