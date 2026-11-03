import csv
import json

import pytest

from tta_capstone_project.ingest import count_queues, main, read_tickets, write_json

FIELDS = ['subject', 'body', 'queue', 'language']


def make_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def ticket(queue, i=0):
    return {'subject': f'Subject {i}', 'body': f'Body {i}', 'queue': queue, 'language': 'en'}


# ---------- read_tickets ----------

def test_read_tickets_returns_dicts_keyed_by_header(tmp_path):
    path = make_csv(tmp_path / 't.csv', [ticket('Billing', 1)])
    assert read_tickets(path) == [ticket('Billing', 1)]


def test_read_tickets_respects_limit(tmp_path):
    path = make_csv(tmp_path / 't.csv', [ticket('IT', i) for i in range(150)])
    rows = read_tickets(path, limit=100)
    assert len(rows) == 100
    assert rows[-1]['subject'] == 'Subject 99'


def test_read_tickets_fewer_rows_than_limit(tmp_path):
    path = make_csv(tmp_path / 't.csv', [ticket('IT', i) for i in range(5)])
    assert len(read_tickets(path, limit=100)) == 5


def test_read_tickets_header_only(tmp_path):
    path = make_csv(tmp_path / 't.csv', [])
    assert read_tickets(path) == []


def test_read_tickets_handles_quoted_commas_and_newlines(tmp_path):
    row = {'subject': 'Hi, there', 'body': 'line1\nline2', 'queue': 'Support', 'language': 'en'}
    path = make_csv(tmp_path / 't.csv', [row])
    assert read_tickets(path) == [row]


def test_read_tickets_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_tickets(tmp_path / 'missing.csv')


# ---------- write_json ----------

def test_write_json_round_trip(tmp_path):
    tickets = [ticket('Billing', 1), ticket('IT', 2)]
    out = tmp_path / 'out.json'
    write_json(tickets, out)
    assert json.loads(out.read_text(encoding='utf-8')) == tickets


def test_write_json_keeps_non_ascii_unescaped(tmp_path):
    tickets = [{'subject': 'Störung', 'body': '問題', 'queue': 'Técnico', 'language': 'de'}]
    out = tmp_path / 'out.json'
    write_json(tickets, out)
    text = out.read_text(encoding='utf-8')
    assert 'Störung' in text and '問題' in text
    assert '\\u' not in text


def test_write_json_is_indented(tmp_path):
    out = tmp_path / 'out.json'
    write_json([ticket('IT')], out)
    assert '\n  {' in out.read_text(encoding='utf-8')


# ---------- count_queues ----------

def test_count_queues_counts_each_queue():
    tickets = [ticket('IT'), ticket('Billing'), ticket('IT'), ticket('IT')]
    assert count_queues(tickets) == {'IT': 3, 'Billing': 1}


def test_count_queues_empty():
    assert count_queues([]) == {}


def test_count_queues_preserves_first_seen_order():
    tickets = [ticket('B'), ticket('A'), ticket('B'), ticket('C')]
    assert list(count_queues(tickets)) == ['B', 'A', 'C']


def test_count_queues_is_case_sensitive():
    assert count_queues([ticket('IT'), ticket('it')]) == {'IT': 1, 'it': 1}


def test_count_queues_missing_queue_key_raises():
    with pytest.raises(KeyError):
        count_queues([{'subject': 'no queue'}])


def test_count_queues_prints_each_queue_as_json(capsys):
    count_queues([ticket('IT'), ticket('Billing')])
    assert capsys.readouterr().out.splitlines() == ['"IT"', '"Billing"']


# ---------- main (end to end) ----------

def test_main_full_run(tmp_path, capsys):
    rows = [ticket('IT', i) for i in range(60)] + [ticket('Billing', i) for i in range(60, 120)]
    csv_path = make_csv(tmp_path / 't.csv', rows)
    json_path = tmp_path / 'out.json'

    counts = main(csv_path, json_path, limit=100)

    assert counts == {'IT': 60, 'Billing': 40}
    assert len(json.loads(json_path.read_text(encoding='utf-8'))) == 100
    out = capsys.readouterr().out
    assert 'IT: 60' in out
    assert 'Billing: 40' in out
    assert 'All rows processed successfully.' in out
    assert 'Total rows processed: 100' in out


def test_main_fewer_rows_than_limit_skips_success_message(tmp_path, capsys):
    csv_path = make_csv(tmp_path / 't.csv', [ticket('IT', i) for i in range(10)])
    counts = main(csv_path, tmp_path / 'out.json', limit=100)

    assert counts == {'IT': 10}
    assert 'All rows processed successfully.' not in capsys.readouterr().out
