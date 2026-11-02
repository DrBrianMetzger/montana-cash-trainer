"""Phase 1 + MVP Phase 2: verified provenance, import, matrix, exact combos."""
import json
import streamlit as st
from solver_repository import SolverRepository
from solver_import import import_json
from solver_models import hand_classes,cap_warning
from range_matrix import render_matrix
from combo_explorer import combo_rows

@st.cache_resource
def repository(): return SolverRepository()

def render_solver_explorer():
    st.subheader('Solver Explorer · structured data')
    st.caption('Only documented MCT JSON interchange files are accepted. Native GTO+ .gto2 files and screenshots cannot be decoded here. A user-verified label is a provenance assertion, not independent authentication.')
    repo=repository()
    upload_tab,explore_tab,backup_tab=st.tabs(['Import solution','Explore strategies','Backup / restore'])
    with upload_tab:
        up=st.file_uploader('Structured solver JSON',type=['json'],key='solver_import_upload')
        if up and st.button('Validate and import',key='solver_import_button'):
            try:
                sol=import_json(up.getvalue().decode('utf-8'))
                if sol['source']['verification']=='synthetic_test': raise ValueError('Synthetic test fixtures cannot be imported into the production library.')
                repo.save(sol)
                st.success(f"Imported {sol['id']} ({len(sol['nodes'])} node(s)).")
            except (ValueError,TypeError,KeyError) as e: st.error(str(e))
        with st.expander('JSON format and provenance'):
            st.write('Required fields: schema, id, solver, source, assumptions, nodes. Each node contains exact combo weights and per-action percentages. Use the bundled synthetic fixture only for automated tests, not production strategy study.')
    with explore_tab:
        items=repo.list()
        if not items: st.info('No structured solutions imported. Your existing GTO+ screenshot library is still available in its own tab.')
        else:
            ids=[x['id'] for x in items]
            selected=st.selectbox('Solution',ids,key='solver_solution_select')
            sol=repo.load(selected)
            st.write('**Source:**',sol['source']['reference'],'· **Verification:**',sol['source']['verification'])
            st.write('**Solver:**',sol['solver']['name'],sol['solver']['version'])
            with st.expander('Complete imported assumptions'):
                st.json(sol['assumptions'])
            st.warning(cap_warning(sol))
            node_ids=[n['id'] for n in sol['nodes']]
            node_id=st.selectbox('Decision node',node_ids,key='solver_node_select')
            node=next(n for n in sol['nodes'] if n['id']==node_id)
            st.write(f"**{node['street']}** · {node['acting_position']} to act · pot {node['pot_bb']} BB · board {' '.join(node['board']) or 'Preflop'}")
            st.caption('Available actions: '+', '.join(node['actions']))
            st.caption('Action history: '+str(node['history']))
            render_matrix(node)
            choices=sorted({__import__('solver_models').hand_class(k.split()) for k in node['combos']})
            if choices:
                hand=st.selectbox('Select a populated hand class',choices,key='solver_hand_select')
                rows=combo_rows(node,hand)
                st.dataframe(rows,use_container_width=True,hide_index=True)
                st.caption('EV and equity appear only if supplied by the imported source. Missing combinations are not inferred.')
            else:st.info('This node has no exact combinations.')
            children=[n['id'] for n in sol['nodes'] if n['parent_id']==node_id]
            st.caption('Stored child nodes: '+(', '.join(children) if children else 'No continuation available'))
            if st.button('Delete selected solution',key='solver_delete'):
                repo.delete(selected);st.rerun()
    with backup_tab:
        st.download_button('Export solver database',repo.backup(),file_name='mct_solver_backup.json',mime='application/json')
        up=st.file_uploader('Restore solver backup',type=['json'],key='solver_restore_upload')
        if up and st.button('Restore solver library',key='solver_restore_button'):
            try:
                obj=json.loads(up.getvalue())
                if any(s.get('source',{}).get('verification')=='synthetic_test' for s in obj.get('solutions',[])):
                    raise ValueError('Synthetic fixtures cannot be restored to the production library.')
                st.success(f"Restored {repo.restore(up.getvalue())} solutions")
            except (ValueError,TypeError,KeyError) as e: st.error(str(e))
        st.warning('SQLite on Streamlit Community Cloud is not guaranteed to persist after redeployments. Download backups regularly.')
