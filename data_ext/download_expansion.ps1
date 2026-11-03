# Expansion datasets for the online (Setting 2) experiment: same problems, two models.
$d = "paper4/data_ext"
$targets = @()
foreach ($task in "MATH500", "GPQA", "MMLU", "MMLU-Pro") {
  foreach ($m in "8B", "70B") {
    $targets += ,@("hazyresearch/${task}_with_Llama_3.1_${m}_Instruct_v1", "weaver_${task}_${m}")
  }
}
$mb = "ScalingIntelligence/monkey_business"
foreach ($cfg in "MiniF2F-MATH_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-70B-Instruct", "GSM8K_Llama-3-70B-Instruct") {
  $u = "https://huggingface.co/api/datasets/$mb/parquet/$cfg/test/0.parquet"
  curl.exe -sSL --retry 3 -o "$d/mb_$cfg.parquet" $u
  "{0}: {1:N1} MB" -f $cfg, ((Get-Item "$d/mb_$cfg.parquet").Length / 1MB)
}
foreach ($t in $targets) {
  $api = Invoke-RestMethod "https://huggingface.co/api/datasets/$($t[0])/parquet"
  $urls = @()
  foreach ($cfg in $api.PSObject.Properties) { foreach ($sp in $cfg.Value.PSObject.Properties) { $urls += $sp.Value } }
  $i = 0
  foreach ($u in $urls) {
    $f = "$d/$($t[1])_$i.parquet"
    curl.exe -sSL --retry 3 -o $f $u
    "{0}: {1:N1} MB" -f $f, ((Get-Item $f).Length / 1MB)
    $i++
  }
}
"done"
