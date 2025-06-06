CREATE TABLE IF NOT EXISTS agent_connected_times
(
    id            SERIAL PRIMARY KEY,
    fecha         DATE         NOT NULL,
    email         VARCHAR(255) NOT NULL,
    total_seconds INTEGER      NOT NULL    DEFAULT 0,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_fecha_email UNIQUE (fecha, email)
);

-- Índices para mejorar performance
CREATE INDEX idx_agent_connected_times_fecha ON agent_connected_times (fecha);
CREATE INDEX idx_agent_connected_times_email ON agent_connected_times (email);
CREATE INDEX idx_agent_connected_times_fecha_email ON agent_connected_times (fecha, email);