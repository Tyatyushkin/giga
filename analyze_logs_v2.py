#!/usr/bin/env python3
"""Глубокий анализ логов GigaCode v2 — поиск узких мест и оптимизаций."""

import json
import glob
import os
import sys
from datetime import datetime
from collections import defaultdict

LOGS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_logs():
    """Загружает все JSON логи в хронологическом порядке."""
    pattern = os.path.join(LOGS_DIR, "openai-*.json")
    files = sorted(glob.glob(pattern))
    logs = []
    for f in files:
        try:
            with open(f, 'r') as fh:
                data = json.load(fh)
                data['_file'] = os.path.basename(f)
                logs.append(data)
        except Exception as e:
            print(f"⚠️  Ошибка чтения {f}: {e}", file=sys.stderr)
    return logs


def extract_agent_type(log):
    """Определяет тип агента по системному промпту."""
    messages = log.get('request', {}).get('messages', [])
    for msg in messages:
        if msg.get('role') == 'system':
            content = msg.get('content', '')
            if 'qa-designer' in content.lower() or 'test case' in content.lower():
                return 'qa-designer'
            elif 'test-critic' in content.lower() or 'review' in content.lower():
                return 'test-critic'
            elif 'requirements-analyst' in content.lower():
                return 'requirements-analyst'
            elif 'pytest-stub-writer' in content.lower() or 'pytest' in content.lower():
                return 'pytest-writer'
            elif 'orchestrat' in content.lower():
                return 'orchestrator'
            elif 'critic' in content.lower():
                return 'test-critic'
    # По инструментальным вызовам
    response = log.get('response', {}).get('choices', [{}])[0].get('message', {})
    tool_calls = response.get('tool_calls', [])
    for tc in tool_calls:
        func = tc.get('function', {})
        name = func.get('name', '')
        args = func.get('arguments', '')
        if name == 'agent':
            try:
                args_dict = json.loads(args) if isinstance(args, str) else args
                sub = args_dict.get('subagent_type', '')
                if sub:
                    return sub
            except:
                pass
    return 'unknown'


def extract_tool_calls(log):
    """Извлекает инструменты из ответа."""
    response = log.get('response', {}).get('choices', [{}])[0].get('message', {})
    tool_calls = response.get('tool_calls', [])
    tools = []
    for tc in tool_calls:
        func = tc.get('function', {})
        tools.append({
            'name': func.get('name', 'unknown'),
            'args_preview': func.get('arguments', '')[:200]
        })
    return tools


def analyze_token_efficiency(log):
    """Анализирует эффективность использования токенов."""
    usage = log.get('response', {}).get('usage', {})
    if not usage:
        return None
    prompt = usage.get('prompt_tokens', 0)
    completion = usage.get('completion_tokens', 0)
    cached = usage.get('prompt_tokens_details', {}).get('cached_tokens', 0)
    
    return {
        'prompt_tokens': prompt,
        'completion_tokens': completion,
        'cached_tokens': cached,
        'cache_hit_rate': cached / prompt if prompt > 0 else 0,
        'total_tokens': prompt + completion,
        'output_ratio': completion / prompt if prompt > 0 else 0
    }


def main():
    print("=" * 80)
    print("GigaCode Logs Analysis v2 — Deep Dive")
    print("=" * 80)
    
    logs = load_logs()
    if not logs:
        print("❌ Логи не найдены")
        return
    
    total_requests = len(logs)
    print(f"\n📊 Всего запросов: {total_requests}")
    
    # 1. Временные диапазоны
    timestamps = []
    for log in logs:
        ts_str = log.get('timestamp', '')
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                pass
    
    if timestamps:
        first = timestamps[0]
        last = timestamps[-1]
        span = (last - first).total_seconds()
        print(f"⏱  Диапазон: {first} → {last}")
        print(f"⏱  Общее время: {span:.0f}s ({span/60:.1f} мин)")
    
    # 2. Распределение по агентам
    agent_dist = defaultdict(int)
    agent_requests = defaultdict(list)
    for i, log in enumerate(logs):
        agent = extract_agent_type(log)
        agent_dist[agent] += 1
        agent_requests[agent].append((i, log))
    
    print(f"\n🤖 Распределение по агентам:")
    for agent, count in sorted(agent_dist.items(), key=lambda x: -x[1]):
        print(f"   {agent:25s}: {count:4d} req ({count/total_requests*100:.1f}%)")
    
    # 3. Эффективность токенов
    print(f"\n📈 Анализ токенов:")
    total_prompt = 0
    total_completion = 0
    total_cached = 0
    agent_tokens = defaultdict(lambda: {'prompt': 0, 'completion': 0, 'cached': 0})
    
    for log in logs:
        eff = analyze_token_efficiency(log)
        if eff:
            total_prompt += eff['prompt_tokens']
            total_completion += eff['completion_tokens']
            total_cached += eff['cached_tokens']
            agent = extract_agent_type(log)
            agent_tokens[agent]['prompt'] += eff['prompt_tokens']
            agent_tokens[agent]['completion'] += eff['completion_tokens']
            agent_tokens[agent]['cached'] += eff['cached_tokens']
    
    cache_rate = total_cached / total_prompt if total_prompt > 0 else 0
    print(f"   Входящих токенов:     {total_prompt:>12,}")
    print(f"   Исходящих токенов:    {total_completion:>12,}")
    print(f"   Закешированных:       {total_cached:>12,}")
    print(f"   Cache hit rate:       {cache_rate*100:.1f}%")
    print(f"   avg output/prompt:    {total_completion/total_prompt*100:.2f}%")
    
    print(f"\n   Токены по агентам:")
    for agent, tokens in sorted(agent_tokens.items(), key=lambda x: -x[1]['prompt']):
        cr = tokens['cached'] / tokens['prompt'] * 100 if tokens['prompt'] > 0 else 0
        ratio = tokens['completion'] / tokens['prompt'] * 100 if tokens['prompt'] > 0 else 0
        print(f"      {agent:25s}: in={tokens['prompt']:>10,}  out={tokens['completion']:>7,}  cache={cr:5.1f}%  ratio={ratio:5.2f}%")
    
    # 4. Анализ интервалов между запросами
    print(f"\n⏱  Анализ интервалов:")
    gaps = []
    for i in range(1, len(timestamps)):
        gap = (timestamps[i] - timestamps[i-1]).total_seconds()
        gaps.append((i, gap, logs[i]))
    
    if gaps:
        avg_gap = sum(g for _, g, _ in gaps) / len(gaps)
        max_gap = max(gaps, key=lambda x: x[1])
        min_gap = min(gaps, key=lambda x: x[1])
        
        print(f"   Средний интервал:     {avg_gap:.1f}s")
        print(f"   Минимальный:          {min_gap[1]:.1f}s (запрос {min_gap[0]})")
        print(f"   Максимальный:         {max_gap[1]:.1f}s (запрос {max_gap[0]})")
        
        # Распределение интервалов
        buckets = {'0-5s': 0, '5-15s': 0, '15-30s': 0, '30-60s': 0, '1-3min': 0, '3-10min': 0, '>10min': 0}
        for idx, gap, _ in gaps:
            if gap < 5:
                buckets['0-5s'] += 1
            elif gap < 15:
                buckets['5-15s'] += 1
            elif gap < 30:
                buckets['15-30s'] += 1
            elif gap < 60:
                buckets['30-60s'] += 1
            elif gap < 180:
                buckets['1-3min'] += 1
            elif gap < 600:
                buckets['3-10min'] += 1
            else:
                buckets['>10min'] += 1
        
        print(f"\n   Распределение интервалов:")
        for bucket, count in buckets.items():
            pct = count / len(gaps) * 100
            bar = '█' * int(pct / 2)
            print(f"      {bucket:>8s}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # 5. Топ-10 самых долгих интервалов — детальный анализ
    print(f"\n🔍 Топ-15 самых долгих интервалов (не модельное время):")
    top_gaps = sorted(gaps, key=lambda x: -x[1])[:15]
    for idx, gap, log in top_gaps:
        agent = extract_agent_type(log)
        tools = extract_tool_calls(log)
        eff = analyze_token_efficiency(log)
        
        tool_names = [t['name'] for t in tools]
        tool_str = ', '.join(tool_names) if tool_names else 'no tools'
        
        cache_pct = eff['cache_hit_rate'] * 100 if eff else 0
        
        print(f"   #{idx:>3d}  {gap:6.1f}s  agent={agent:20s}  tools=[{tool_str}]  cache={cache_pct:5.1f}%  out={eff['completion_tokens'] if eff else 0:5d}")
        
        # Покажем context windows для самых больших
        if gap > 60:
            messages = log.get('request', {}).get('messages', [])
            total_chars = sum(len(str(m.get('content', ''))) for m in messages)
            print(f"         context: {len(messages)} messages, ~{total_chars:,} chars system+user")
    
    # 6. Анализ tool calls
    print(f"\n🔧 Анализ инструментов:")
    tool_usage = defaultdict(int)
    for log in logs:
        tools = extract_tool_calls(log)
        for t in tools:
            tool_usage[t['name']] += 1
    
    for tool, count in sorted(tool_usage.items(), key=lambda x: -x[1]):
        pct = count / total_requests * 100
        print(f"   {tool:25s}: {count:4d} ({pct:5.1f}%)")
    
    # 7. Анализ оркестратора — batch calls
    print(f"\n📦 Параллельные вызовы (batch):")
    batch_count = 0
    max_batch_size = 0
    for i, log in enumerate(logs):
        tools = extract_tool_calls(log)
        # Ищем agent calls в инструментах
        agent_calls = [t for t in tools if t['name'] == 'agent']
        if len(agent_calls) > 1:
            batch_count += 1
            max_batch_size = max(max_batch_size, len(agent_calls))
            # Показываем первый agent call
            first = agent_calls[0]
            args = first.get('args_preview', '')
            try:
                args_dict = json.loads(args) if isinstance(args, str) else args
                sub = args_dict.get('subagent_type', '')
                desc = args_dict.get('description', '')[:50]
                print(f"   batch@#{i}: {len(agent_calls)} agents → sub={sub}, desc={desc}")
            except:
                pass
    
    print(f"   Batch-вызовов (>1 agent): {batch_count}")
    print(f"   Макс. размер батча:      {max_batch_size}")
    
    # 8. Анализ эффективности по фазам
    print(f"\n📊 Анализ по фазам:")
    phases = {
        'Phase 1 (requirements-analyst)': [],
        'Phase 2.5 (qa-designer)': [],
        'Phase 3 (test-critic)': [],
        'Phase 4 (pytest-writer)': [],
        'orchestrator/gate': []
    }
    phase_map = {
        'requirements-analyst': 'Phase 1 (requirements-analyst)',
        'qa-designer': 'Phase 2.5 (qa-designer)',
        'test-critic': 'Phase 3 (test-critic)',
        'pytest-writer': 'Phase 4 (pytest-writer)',
        'orchestrator': 'orchestrator/gate'
    }
    
    for i, log in enumerate(logs):
        agent = extract_agent_type(log)
        phase = phase_map.get(agent, 'unknown')
        eff = analyze_token_efficiency(log)
        if eff:
            phases[phase].append((i, eff, log))
    
    for phase, reqs in phases.items():
        if not reqs:
            continue
        total_out = sum(e[1]['completion_tokens'] for _, e, _ in reqs)
        total_in = sum(e[1]['prompt_tokens'] for _, e, _ in reqs)
        avg_out = total_out / len(reqs)
        avg_in = total_in / len(reqs)
        print(f"   {phase:35s}: {len(reqs):3d} req, avg in={avg_in:>8,.0f}, avg out={avg_out:>7,.0f}, total out={total_out:>9,}")
    
    # 9. Ключевые метрики для оптимизации
    print(f"\n{'='*80}")
    print("🎯 КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ ДЛЯ ОПТИМИЗАЦИИ:")
    print(f"{'='*80}")
    
    # Находим агентов с самым большим контекстом
    print(f"\n1. Агенты с самым большим средним контекстом (prompt_tokens):")
    agent_avg_prompt = {}
    for agent, reqs in agent_requests.items():
        total_p = 0
        count = 0
        for _, log in reqs:
            eff = analyze_token_efficiency(log)
            if eff:
                total_p += eff['prompt_tokens']
                count += 1
        if count > 0:
            agent_avg_prompt[agent] = total_p / count
    
    for agent, avg in sorted(agent_avg_prompt.items(), key=lambda x: -x[1])[:5]:
        print(f"   {agent:25s}: {avg:10,.0f} avg prompt tokens")
    
    # Находим запросы с самым низким output/prompt ratio
    print(f"\n2. Запросы с самым низким соотношением output/prompt (дорогой контекст):")
    inefficient = []
    for i, log in enumerate(logs):
        eff = analyze_token_efficiency(log)
        if eff and eff['prompt_tokens'] > 1000:
            inefficient.append((i, eff, extract_agent_type(log)))
    
    inefficient.sort(key=lambda x: x[1]['output_ratio'])
    for idx, eff, agent in inefficient[:10]:
        print(f"   #{idx:>3d}  ratio={eff['output_ratio']:.4f}  in={eff['prompt_tokens']:>8,}  out={eff['completion_tokens']:>6,}  agent={agent}")
    
    # Находим паттерн: чтение файлов → большие интервалы
    print(f"\n3. Паттерн: read_file / read_many_calls перед большими интервалами:")
    for idx, gap, log in top_gaps[:5]:
        if idx > 0:
            prev_log = logs[idx - 1]
            prev_tools = extract_tool_calls(prev_log)
            tool_names = [t['name'] for t in prev_tools]
            if any(t in tool_names for t in ['read_file', 'read_many_files', 'glob', 'grep_search']):
                print(f"   Перед интервалом {gap:.1f}s (#{idx}) был tool: {tool_names}")


if __name__ == '__main__':
    main()
