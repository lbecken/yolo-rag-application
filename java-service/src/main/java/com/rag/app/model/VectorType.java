package com.rag.app.model;

import org.hibernate.engine.spi.SharedSessionContractImplementor;
import org.hibernate.usertype.UserType;
import org.postgresql.util.PGobject;
import java.io.Serializable;
import java.sql.*;

// Handle Postgres vector type in Hibernate
public class VectorType implements UserType<float[]> {

    @Override
    public int getSqlType() {
        return Types.OTHER;
    }

    @Override
    public Class<float[]> returnedClass() {
        return float[].class;
    }

    @Override
    public boolean equals(float[] x, float[] y) {
        return java.util.Arrays.equals(x, y);
    }

    @Override
    public int hashCode(float[] x) {
        return java.util.Arrays.hashCode(x);
    }

    @Override
    public float[] nullSafeGet(ResultSet rs, int position, SharedSessionContractImplementor session, Object owner) 
            throws SQLException {
        String pgVector = rs.getString(position);
        if (pgVector == null) {
            return null;
        }
        // Parse PostgreSQL vector format: "[0.1,0.2,0.3]"
        String[] values = pgVector.replace("[", "").replace("]", "").split(",");
        float[] result = new float[values.length];
        for (int i = 0; i < values.length; i++) {
            result[i] = Float.parseFloat(values[i].trim());
        }
        return result;
    }

    @Override
    public void nullSafeSet(PreparedStatement st, float[] value, int index, SharedSessionContractImplementor session) 
            throws SQLException {
        if (value == null) {
            st.setNull(index, Types.OTHER);
        } else {
            // Convert float array to PostgreSQL vector format: "[0.1,0.2,0.3]"
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < value.length; i++) {
                if (i > 0) sb.append(",");
                sb.append(value[i]);
            }
            sb.append("]");
            
            // Cast to vector type
            PGobject pgObject = new PGobject();
            pgObject.setType("vector");
            pgObject.setValue(sb.toString());
            st.setObject(index, pgObject);
        }
    }

    @Override
    public float[] deepCopy(float[] value) {
        return value == null ? null : value.clone();
    }

    @Override
    public boolean isMutable() {
        return true;
    }

    @Override
    public Serializable disassemble(float[] value) {
        return deepCopy(value);
    }

    @Override
    public float[] assemble(Serializable cached, Object owner) {
        return deepCopy((float[]) cached);
    }
}
