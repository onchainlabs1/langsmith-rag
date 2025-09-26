# 📊 **GRAFANA SETUP GUIDE - EU AI Act RAG System**

## 🎯 **Status: ✅ FUNCIONANDO**

O Grafana está agora rodando corretamente! Aqui está o guia completo para configurar os dashboards.

## 🚀 **Acesso Rápido**

```bash
# URLs de Acesso
Grafana:     http://localhost:3000 (admin/admin)
Prometheus:  http://localhost:9090
Jaeger:      http://localhost:16686 (se ativado)

# Comandos Úteis
./monitoring/access_urls.sh          # Ver todas as URLs
docker compose -f docker-compose-simple.yml logs -f  # Ver logs
docker compose -f docker-compose-simple.yml down     # Parar serviços
```

## 📋 **Configuração Manual do Dashboard**

### 1. **Login no Grafana**
- Acesse: http://localhost:3000
- Usuário: `admin`
- Senha: `admin`

### 2. **Adicionar Prometheus como Data Source**
1. Vá em **Configuration** → **Data Sources**
2. Clique **Add data source**
3. Selecione **Prometheus**
4. URL: `http://prometheus:9090` (ou `http://localhost:9090`)
5. Clique **Save & Test**

### 3. **Criar Dashboard RAG System**
1. Vá em **+** → **Dashboard**
2. Clique **Add visualization**

#### **Painel 1: Request Rate**
- **Query**: `rate(rag_requests_total[5m])`
- **Title**: "Request Rate (req/sec)"
- **Unit**: "req/sec"

#### **Painel 2: Response Time (p95)**
- **Query**: `histogram_quantile(0.95, rate(rag_request_duration_seconds_bucket[5m]))`
- **Title**: "Response Time 95th Percentile"
- **Unit**: "s"

#### **Painel 3: Error Rate**
- **Query**: `rate(rag_errors_total[5m])`
- **Title**: "Error Rate (errors/sec)"
- **Unit**: "errors/sec"

#### **Painel 4: Citation Validity**
- **Query**: `histogram_quantile(0.50, rag_citation_validity_score_bucket)`
- **Title**: "Citation Validity Score"
- **Unit**: "percentunit"
- **Min**: 0, **Max**: 1

### 4. **Salvar Dashboard**
1. Clique **Save dashboard**
2. Nome: "EU AI Act RAG System"
3. Tags: `rag`, `ai-act`, `monitoring`

## 🔧 **Métricas Disponíveis**

Quando o sistema RAG estiver rodando, você verá estas métricas no Prometheus:

```
# Request Metrics
rag_requests_total
rag_request_duration_seconds

# Error Metrics  
rag_errors_total

# Token Metrics
rag_input_tokens_total
rag_output_tokens_total

# Cost Metrics
rag_cost_usd_total

# Citation Metrics
rag_citation_validity_score
rag_citations_per_response

# Stage Metrics
rag_retrieval_duration_seconds
rag_generation_duration_seconds
rag_postprocess_duration_seconds
```

## 🚨 **Troubleshooting**

### **Grafana não carrega**
```bash
# Verificar status
docker ps | grep grafana

# Ver logs
docker compose -f docker-compose-simple.yml logs grafana

# Reiniciar
docker compose -f docker-compose-simple.yml restart grafana
```

### **Prometheus não conecta**
```bash
# Verificar se Prometheus está rodando
curl http://localhost:9090

# Ver logs
docker compose -f docker-compose-simple.yml logs prometheus
```

### **Sem métricas aparecendo**
- Certifique-se que o sistema RAG está rodando
- Verifique se as métricas estão sendo expostas em `/metrics`
- Confirme que o Prometheus está fazendo scrape do endpoint correto

## 📈 **Próximos Passos**

1. **Iniciar o Sistema RAG**:
   ```bash
   source setup_tracing.sh
   uvicorn src.main:app --reload --port 8000
   ```

2. **Testar Métricas**:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. **Fazer Queries** para gerar métricas:
   ```bash
   curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the EU AI Act?"}'
   ```

## 🎉 **Sucesso!**

O Grafana está funcionando e pronto para monitorar o sistema RAG. Quando você iniciar o sistema RAG e fizer algumas queries, as métricas aparecerão automaticamente nos dashboards configurados.

---

**Criado em**: 2025-09-25  
**Status**: ✅ Funcionando  
**Versão**: 1.0
