from mysqlconnection import connectToMySQL


class Report:

    @classmethod
    def save(
        cls,
        usuario_id,
        tipo_reporte,
        elemento_tipo,
        elemento_id,
        motivo,
        descripcion
    ):

        if not motivo:
            raise ValueError("Debes seleccionar un motivo")

        if not descripcion:
            raise ValueError("Debes describir el problema")

        query = """
            INSERT INTO reportes (
                usuario_id,
                tipo_reporte,
                elemento_tipo,
                elemento_id,
                motivo,
                descripcion
            )
            VALUES (
                %(usuario_id)s,
                %(tipo_reporte)s,
                %(elemento_tipo)s,
                %(elemento_id)s,
                %(motivo)s,
                %(descripcion)s
            );
        """

        data = {
            "usuario_id": usuario_id,
            "tipo_reporte": tipo_reporte,
            "elemento_tipo": elemento_tipo,
            "elemento_id": elemento_id,
            "motivo": motivo,
            "descripcion": descripcion
        }

        return connectToMySQL('almaceb_red').query_db(
            query,
            data
        )