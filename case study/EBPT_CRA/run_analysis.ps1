# PowerShell helper to run the 50-node analysis pipeline

$script = Join-Path -Path $PSScriptRoot -ChildPath 'scripts\analyze_top_tier_results.py'
$input = Join-Path -Path $PSScriptRoot -ChildPath '..\top_tier_results\results_50nodes.json'
$out = Join-Path -Path $PSScriptRoot -ChildPath '..\top_tier_results\analysis_50nodes'

python $script --input $input --outdir $out --expected-seeds 30
