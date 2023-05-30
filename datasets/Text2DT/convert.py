import os, json

rel_label_mapping = {
    "临床表现": "临床表现",
    "治疗药物": "用药",
    "治疗方案": "治疗方案",
    "用法用量": "用法",
    "基本情况": "基本情况",
    "禁用药物": "慎用",
}

def preorder_traverse(tree, start, list_triple2relID, relations, side='left', TreeS=False):
    if start >= len(tree):
        return None, ''

    root = tree[start]
    triple2relID = list_triple2relID[start]
    role = root['role']
    tgt_seq = ''

    if role == 'C':
        if side == 'left':
            tgt_seq += '若'
        else:
            tgt_seq += '否则，若'

        tgt_seq += read_node(root, triple2relID, relations, TreeS)
        tgt_seq += '，'

        left_end, left_tgt_seq = preorder_traverse(tree, start+1, list_triple2relID, relations, TreeS=TreeS)
        tgt_seq += left_tgt_seq

        right_end, right_tgt_seq = preorder_traverse(tree, left_end+1, list_triple2relID, relations, side='right', TreeS=TreeS)
        tgt_seq += right_tgt_seq

        end = right_end

    elif role == 'D':
        if len(root['triples']) > 0:
            if side == 'left':
                tgt_seq += '则'
            else:
                tgt_seq += '否则'

            tgt_seq += read_node(root, triple2relID, relations, TreeS)
            tgt_seq += '，' if any([len(x['triples']) > 0 for x in tree[start+1:]]) else '。'
        
        end = start

    return end, tgt_seq


def read_node(node, triple2relID, relations, TreeS=False):
    role = node['role']
    triples = [tuple(t) for t in node['triples']]
    logical_rel = node['logical_rel']

    if logical_rel == 'or':
        conjunction = '或'
    elif role == 'C':
        conjunction = '且'
    else:
        conjunction = '和'

    clauses = []
    visited = set()
    for i, t1 in enumerate(triples):
        if t1 in visited:
            continue
        id1 = triple2relID[t1]

        clause = [id1]
        visited.add(t1)

        for t2 in triples[i+1:]:
            if t2 in visited:
                continue

            if t1[-1] == t2[0] or t1[0] == t2[-1]:
                id2 = triple2relID[t2]
                clause.append(id2)
                visited.add(t2)

        # if len(clause) > 2:
        #     print([relations[id] for id in clause])

        try:
            clause = sorted(clause, key=lambda x: location(x, relations))
        except:
            pass

        clauses.append(clause)

    try:
        clauses = sorted(clauses, key=lambda x: clause_location(x, relations))
    except:
        pass

    if TreeS:
        clauses = conjunction.join(['...' for clause in clauses])
    else:
        clauses = conjunction.join([''.join([linearize_triple(relations[x]) for x in clause]) for clause in clauses])

    return clauses

def location(relID, relations):
    rel = relations[relID]
    return sum(rel[0][:2] + rel[2][:2])
    # return (sum(rel[2][:2]), sum(rel[0][:2]))

def clause_location(clause, relations):
    return min([location(relID, relations) for relID in clause])

# def linearize_clause(clause, relations):
#     for tripleID in clause:
#         triple = relations[tripleID]
#     return

def linearize_triple(triple):
    return '('+ triple[0][-1] + ', ' + rel_label_mapping[triple[1]] + ', ' + triple[2][-1] + ')'


def convert_sample(input_doc, RE=False, TreeS=False):
    samples = []

    with open(input_doc) as f:
        lines = f.readlines()
        lines = [eval(ele) for ele in lines]
    for idx, line in enumerate(lines):
        # print(line)
        text = line["text"]
        tree = line["tree"]
        triples = line["relations"]
        
        list_triple2relID = []
        visited = set()
        for node in tree:
            triple2relID = dict()
            for triple in node['triples']:
                triple = tuple(triple)
                candidates = []
                for relID, rel in enumerate(line["relations"]):
                    if (rel[0][-1], rel[1], rel[2][-1]) == triple:
                        candidates.append(relID)
                        if relID not in visited:
                            triple2relID[triple] = relID
                            visited.add(relID)
                            break
                if triple not in triple2relID:
                    triple2relID[triple] = candidates[-1]

            list_triple2relID.append(triple2relID)

        _, tgt_seq = preorder_traverse(tree, 0, list_triple2relID, triples)

        sample = {'input': text, 'target': tgt_seq, 'RE_target': '', 'TreeS_target': ''}
        # print(text)
        # print(tgt_seq)

        if RE:
            triples_seq = '[' + ', '.join([linearize_triple(x) for x in triples]) + ']'
            sample['RE_target'] = triples_seq

        if TreeS:
            _, tgt_seq = preorder_traverse(tree, 0, list_triple2relID, triples, TreeS=True)
            sample['TreeS_target'] = tgt_seq

        samples.append(sample)

    return samples

if __name__ == '__main__':
    in_dir = 'raw_data'
    out_dir = './'

    os.makedirs(out_dir, exist_ok=True)

    for root, dirs, files in os.walk(in_dir):
        for fn in files:
            if fn[-4:] != '.txt':
                continue

            print(fn)
            samples = convert_sample(os.path.join(in_dir, fn), RE=True, TreeS=True)
            fname = fn.split('.')[0]

            json_f = open(os.path.join(out_dir, fname + '.json'), 'w', encoding='utf-8')
            for sample in samples:
                json_line = json.dumps(sample, ensure_ascii=False)
                print(json_line, file=json_f)
