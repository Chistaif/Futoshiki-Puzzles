import argparse
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# Thiết lập style chung cho toàn bộ biểu đồ
sns.set_theme(style="whitegrid", context="talk")


def extract_input_order(values: List[str]) -> List[str]:
    """Sắp xếp input_file theo thứ tự số tự nhiên: input-01, input-02, ..."""

    def _key(name: str) -> int:
        digits = "".join(ch for ch in name if ch.isdigit())
        return int(digits) if digits else 10**9

    unique_values = sorted(pd.Series(values).dropna().unique().tolist(), key=_key)
    return unique_values


def save_figure(fig: plt.Figure, filename: str, output_dir: Path) -> None:
    """Lưu biểu đồ một lần vào thư mục output."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    fig.savefig(output_path, bbox_inches="tight")


def prepare_data(csv_path: Path) -> pd.DataFrame:
    """Đọc và làm sạch dữ liệu từ solved.csv."""
    df = pd.read_csv(csv_path)

    # Chuẩn hóa kiểu dữ liệu cho các cột số
    numeric_cols = ["time", "node_expanded", "memory"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Loại bỏ dòng không hợp lệ và các dòng SKIPPED (không có ý nghĩa so sánh hiệu năng)
    df = df.dropna(subset=["input_file", "solver", "time", "memory", "node_expanded"])
    df = df[df["solved"].astype(str).str.upper() != "SKIPPED"].copy()

    return df


def plot_grouped_runtime(df: pd.DataFrame, palette: dict, output_dir: Path) -> None:
    """Grouped Bar Chart so sánh runtime theo input_file và solver (trục Y log)."""
    runtime_df = df[df["time"] > 0].copy()
    input_order = extract_input_order(runtime_df["input_file"].tolist())

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.barplot(
        data=runtime_df,
        x="input_file",
        y="time",
        hue="solver",
        order=input_order,
        palette=palette,
        ax=ax,
    )

    ax.set_yscale("log")
    ax.set_title("Runtime Comparison by Solver and Input")
    ax.set_xlabel("Input File")
    ax.set_ylabel("Execution Time (seconds, log scale)")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Solver", bbox_to_anchor=(1.02, 1), loc="upper left")

    fig.tight_layout()
    save_figure(fig, "grouped_bar_runtime.png", output_dir)
    plt.close(fig)


def plot_memory_vs_time(df: pd.DataFrame, palette: dict, output_dir: Path) -> None:
    """Line chart thể hiện trade-off giữa thời gian chạy và bộ nhớ."""
    tradeoff_df = df[df["time"] > 0].copy()

    # Sắp xếp theo solver + time để đường line có diễn tiến rõ ràng
    tradeoff_df = tradeoff_df.sort_values(["solver", "time"])

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.lineplot(
        data=tradeoff_df,
        x="time",
        y="memory",
        hue="solver",
        style="solver",
        markers=True,
        dashes=False,
        palette=palette,
        linewidth=2,
        ax=ax,
    )

    ax.set_title("Memory vs Time Trade-off")
    ax.set_xlabel("Execution Time (seconds)")
    ax.set_ylabel("Memory Usage (MB)")
    ax.legend(title="Solver", bbox_to_anchor=(1.02, 1), loc="upper left")

    fig.tight_layout()
    save_figure(fig, "line_memory_vs_time.png", output_dir)
    plt.close(fig)


def plot_radar_performance(df: pd.DataFrame, palette: dict, output_dir: Path) -> None:
    """Radar chart cho trung bình time/memory/node_expanded với chuẩn hóa đảo chiều (lower is better)."""
    radar_df = df[df["time"] > 0].copy()

    # Tính trung bình theo solver
    agg = (
        radar_df.groupby("solver", as_index=False)[["time", "memory", "node_expanded"]]
        .mean()
        .rename(
            columns={
                "time": "avg_time",
                "memory": "avg_memory",
                "node_expanded": "avg_node_expanded",
            }
        )
    )

    metrics = ["avg_time", "avg_memory", "avg_node_expanded"]

    # Chuẩn hóa đảo chiều: giá trị gốc càng thấp thì điểm càng cao (0..1)
    for metric in metrics:
        max_val = agg[metric].max()
        min_val = agg[metric].min()
        if np.isclose(max_val, min_val):
            agg[f"score_{metric}"] = 1.0
        else:
            agg[f"score_{metric}"] = (max_val - agg[metric]) / (max_val - min_val)

    score_cols = [f"score_{m}" for m in metrics]
    labels = ["Time (lower is better)", "Memory (lower is better)", "Node Expanded (lower is better)"]

    angles = np.linspace(0, 2 * np.pi, len(score_cols), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"polar": True})

    for solver in agg["solver"]:
        row = agg[agg["solver"] == solver].iloc[0]
        values = [row[col] for col in score_cols]
        values += values[:1]

        color = palette.get(solver)
        ax.plot(angles, values, label=solver, linewidth=2, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_title("Normalized Performance Radar (Higher Area = Better)", pad=20)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    # NHÍCH NHÃN "TIME" SANG PHẢI
    # Lấy danh sách các nhãn trục X
    xticklabels = ax.get_xticklabels()
    for lbl in xticklabels:
        if "Time" in lbl.get_text():
            # Nhích sang phải bằng cách chỉnh position (x, y) 
            # hoặc dùng set_horizontalalignment nếu nhãn đang ở vị trí 0 độ
            lbl.set_ha('left') # Căn lề trái để chữ đẩy sang phải
            lbl.set_position((0.1, 0.05)) # Tinh chỉnh tọa độ (x là nhích ngang, y là nhích dọc)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"])
    ax.set_ylim(0, 1)
    ax.legend(title="Solver", bbox_to_anchor=(1.2, 1.1), loc="upper left")

    fig.tight_layout()
    save_figure(fig, "radar_solver_performance.png", output_dir)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate solver performance graphs from solved.csv")
    parser.add_argument("--csv", default="solved.csv", help="Path to solved.csv")
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory for charts (default: same level as main.py)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    project_root = Path(__file__).resolve().parent
    output_dir = Path(args.out) if args.out else project_root

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = prepare_data(csv_path)
    solver_order = sorted(df["solver"].unique().tolist())
    palette_colors = sns.color_palette("tab10", n_colors=max(len(solver_order), 3))
    palette = {solver: palette_colors[i] for i, solver in enumerate(solver_order)}

    plot_grouped_runtime(df, palette, output_dir)
    plot_memory_vs_time(df, palette, output_dir)
    plot_radar_performance(df, palette, output_dir)

    print("✓ Biểu đồ đã được tạo thành công (Graphs generated successfully)")
    print(f"  - Output: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
