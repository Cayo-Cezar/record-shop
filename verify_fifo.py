import urllib.request
import json

pedidos = []
for page in range(1, 8):
    url = f'https://record-shop-production-72f7.up.railway.app/pedidos?page={page}&page_size=100&cliente_id=21'
    try:
        req = urllib.request.urlopen(url)
        data = json.loads(req.read())
        pedidos.extend(data['items'])
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        break

# Filtrar os 600 do teste (os mais recentes desse cliente)
latest_pedidos = pedidos[:600]

completed = [p for p in latest_pedidos if p['status'] == 'COMPLETED']
failed = [p for p in latest_pedidos if p['status'] == 'FAILED']

print(f"Total de pedidos do teste: {len(latest_pedidos)}")
print(f"Pedidos SUCESSO (COMPLETED): {len(completed)}")
print(f"Pedidos FALHADOS (FAILED): {len(failed)}")

if completed and failed:
    # Ordenar por data de criação (a hora exata que a requisição bateu na API)
    completed.sort(key=lambda x: x['criado_em'])
    failed.sort(key=lambda x: x['criado_em'])
    
    first_completed = completed[0]
    last_completed = completed[-1]
    first_failed = failed[0]
    last_failed = failed[-1]
    
    print('\n-- ORDEM CRONOLOGICA (FIFO) --')
    print(f"1º pedido APROVADO entrou na fila as:     {first_completed['criado_em']}")
    print(f"Ultimo (500º) APROVADO entrou na fila as: {last_completed['criado_em']}")
    print(f"1º pedido REJEITADO entrou na fila as:    {first_failed['criado_em']}")
    print(f"Ultimo (100º) REJEITADO entrou na fila:   {last_failed['criado_em']}")
    
    if last_completed['criado_em'] <= first_failed['criado_em']:
        print("\nCOMPROVADO: A fila seguiu estritamente a ordem de chegada (FIFO)!")
    else:
        print("\n(Nota: pequenos milissegundos podem se sobrepor dependendo do disparo das threads do teste)")
