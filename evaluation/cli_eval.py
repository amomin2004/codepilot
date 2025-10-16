#!/usr/bin/env python3
"""
CodePilot Evaluation CLI

Command-line interface for running evaluations.
"""

import argparse
import sys
from pathlib import Path
from eval import CodePilotEvaluator


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate CodePilot semantic search performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full evaluation with default golden set
  python evaluation/cli_eval.py

  # Run with custom golden set
  python evaluation/cli_eval.py --golden-set custom_goldens.json

  # Run with different API URL
  python evaluation/cli_eval.py --api-url http://localhost:8080

  # Save results to custom file
  python evaluation/cli_eval.py --output custom_results.json

  # Run evaluation and generate report
  python evaluation/cli_eval.py --report
        """
    )
    
    parser.add_argument(
        "--golden-set",
        type=Path,
        default=Path("evaluation/goldens.json"),
        help="Path to golden test set JSON file (default: evaluation/goldens.json)"
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API server URL (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/results.json"),
        help="Output file for detailed results (default: evaluation/results.json)"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML report (requires --output)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.golden_set.exists():
        print(f"❌ Golden set file not found: {args.golden_set}")
        sys.exit(1)
    
    if args.report and not args.output:
        print("❌ --report requires --output to be specified")
        sys.exit(1)
    
    try:
        # Run evaluation
        evaluator = CodePilotEvaluator(args.api_url)
        golden_set = evaluator.load_golden_set(args.golden_set)
        
        if args.verbose:
            print(f"📋 Dataset: {golden_set['dataset_name']}")
            print(f"📁 Repository: {golden_set['repository']}")
            print(f"📊 Queries: {golden_set['total_queries']}")
            print(f"🎯 API URL: {args.api_url}")
            print()
        
        summary = evaluator.evaluate_dataset(golden_set)
        evaluator.print_summary(summary)
        
        # Save results
        evaluator.save_detailed_results(args.output)
        
        # Generate report if requested
        if args.report:
            generate_html_report(summary, args.output)
        
        # Exit with appropriate code
        targets_met = sum(1 for comp in summary.target_comparison.values() if comp["met"])
        total_targets = len(summary.target_comparison)
        
        if targets_met == total_targets:
            print("\n🎉 All evaluation targets achieved!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {total_targets - targets_met} targets missed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Evaluation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def generate_html_report(summary, output_file):
    """Generate HTML report from evaluation results."""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodePilot Evaluation Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2563eb; margin-bottom: 30px; }}
        h2 {{ color: #374151; margin-top: 30px; margin-bottom: 15px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #f8fafc; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1f2937; }}
        .metric-label {{ color: #6b7280; font-size: 14px; margin-top: 5px; }}
        .target-met {{ border-left-color: #10b981; }}
        .target-missed {{ border-left-color: #ef4444; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
        .status-pass {{ color: #10b981; font-weight: bold; }}
        .status-fail {{ color: #ef4444; font-weight: bold; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 CodePilot Evaluation Report</h1>
        
        <h2>📊 Overall Performance</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{summary.total_queries}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            <div class="metric {'target-met' if summary.target_comparison['precision_at_5']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.precision_at_5:.3f}</div>
                <div class="metric-label">Precision@5 (target: {summary.target_comparison['precision_at_5']['target']:.3f})</div>
            </div>
            <div class="metric {'target-met' if summary.target_comparison['precision_at_10']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.precision_at_10:.3f}</div>
                <div class="metric-label">Precision@10 (target: {summary.target_comparison['precision_at_10']['target']:.3f})</div>
            </div>
            <div class="metric {'target-met' if summary.target_comparison['mean_reciprocal_rank']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.mean_reciprocal_rank:.3f}</div>
                <div class="metric-label">Mean Reciprocal Rank (target: {summary.target_comparison['mean_reciprocal_rank']['target']:.3f})</div>
            </div>
        </div>
        
        <h2>⚡ Latency Performance</h2>
        <div class="metrics">
            <div class="metric {'target-met' if summary.target_comparison['latency_p50']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.latency_p50:.1f}ms</div>
                <div class="metric-label">P50 Latency (target: ≤{summary.target_comparison['latency_p50']['target']:.0f}ms)</div>
            </div>
            <div class="metric {'target-met' if summary.target_comparison['latency_p95']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.latency_p95:.1f}ms</div>
                <div class="metric-label">P95 Latency (target: ≤{summary.target_comparison['latency_p95']['target']:.0f}ms)</div>
            </div>
            <div class="metric {'target-met' if summary.target_comparison['latency_p99']['met'] else 'target-missed'}">
                <div class="metric-value">{summary.latency_p99:.1f}ms</div>
                <div class="metric-label">P99 Latency (target: ≤{summary.target_comparison['latency_p99']['target']:.0f}ms)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.latency_mean:.1f}ms</div>
                <div class="metric-label">Mean Latency</div>
            </div>
        </div>
        
        <h2>📁 Performance by Category</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Queries</th>
                    <th>Precision@5</th>
                    <th>Precision@10</th>
                    <th>MRR</th>
                    <th>Avg Latency</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for category, metrics in summary.category_breakdown.items():
        html_content += f"""
                <tr>
                    <td>{category.title()}</td>
                    <td>{metrics['count']}</td>
                    <td>{metrics['precision_at_5']:.3f}</td>
                    <td>{metrics['precision_at_10']:.3f}</td>
                    <td>{metrics['mean_reciprocal_rank']:.3f}</td>
                    <td>{metrics['avg_latency']:.1f}ms</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
        
        <h2>🎚️ Performance by Difficulty</h2>
        <table>
            <thead>
                <tr>
                    <th>Difficulty</th>
                    <th>Queries</th>
                    <th>Precision@5</th>
                    <th>Precision@10</th>
                    <th>MRR</th>
                    <th>Avg Latency</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for difficulty, metrics in summary.difficulty_breakdown.items():
        html_content += f"""
                <tr>
                    <td>{difficulty.title()}</td>
                    <td>{metrics['count']}</td>
                    <td>{metrics['precision_at_5']:.3f}</td>
                    <td>{metrics['precision_at_10']:.3f}</td>
                    <td>{metrics['mean_reciprocal_rank']:.3f}</td>
                    <td>{metrics['avg_latency']:.1f}ms</td>
                </tr>
"""
    
    targets_met = sum(1 for comp in summary.target_comparison.values() if comp["met"])
    total_targets = len(summary.target_comparison)
    
    html_content += f"""
            </tbody>
        </table>
        
        <h2>🎯 Target Summary</h2>
        <div class="metrics">
            <div class="metric {'target-met' if targets_met == total_targets else 'target-missed'}">
                <div class="metric-value">{targets_met}/{total_targets}</div>
                <div class="metric-label">Targets Met</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {summary.total_queries} queries</p>
            <p>CodePilot Evaluation Report</p>
        </div>
    </div>
</body>
</html>
"""
    
    report_file = output_file.with_suffix('.html')
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    print(f"📊 HTML report saved to: {report_file}")


if __name__ == "__main__":
    main()
