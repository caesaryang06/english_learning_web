import mysql.connector
from mysql.connector import Error, pooling
from datetime import datetime, date, timedelta
from config import Config
import os


class DatabaseManager:
    def __init__(self):
        """初始化数据库连接"""
        self.db_config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_DATABASE,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }

        # 创建连接池
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="english_pool",
                pool_size=10,
                **self.db_config
            )
            print("数据库连接池创建成功")
            self.create_tables()
        except Error as e:
            print(f"创建连接池失败: {e}")
            # 如果数据库不存在，先创建
            self._create_database()

    def _create_database(self):
        """创建数据库"""
        try:
            temp_config = self.db_config.copy()
            temp_config.pop('database', None)

            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            connection.close()

            # 重新创建连接池
            self.pool = pooling.MySQLConnectionPool(
                pool_name="english_pool",
                pool_size=10,
                **self.db_config
            )
            print("数据库创建成功")
            self.create_tables()
        except Error as e:
            print(f"创建数据库失败: {e}")

    def get_connection(self):
        """从连接池获取连接"""
        try:
            return self.pool.get_connection()
        except Error as e:
            print(f"获取连接失败: {e}")
            return None

    def create_tables(self):
        """创建数据表"""
        connection = self.get_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    avatar VARCHAR(500),
                    token VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # 学习内容表（添加 user_id）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    type ENUM('word', 'phrase', 'sentence') NOT NULL,
                    english TEXT NOT NULL,
                    chinese TEXT NOT NULL,
                    pronunciation VARCHAR(200),
                    example_en TEXT,
                    example_zh TEXT,
                    audio_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_type (user_id, type),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)


            # 学习记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    learned_date DATE NOT NULL,
                    review_count INT DEFAULT 0,
                    correct_count INT DEFAULT 0,
                    wrong_count INT DEFAULT 0,
                    last_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES learning_items(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_item_date (item_id, learned_date),
                    INDEX idx_item_date (item_id, learned_date),
                    INDEX idx_learned_date (learned_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # 复习内容表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed BOOLEAN DEFAULT FALSE,
                    reviewed_date TIMESTAMP NULL,
                    FOREIGN KEY (item_id) REFERENCES learning_items(id) ON DELETE CASCADE,
                    INDEX idx_item_reviewed (item_id, reviewed),
                    INDEX idx_added_date (added_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            connection.commit()
            cursor.close()
            print("数据表创建成功")
        except Error as e:
            print(f"创建表失败: {e}")
        finally:
            connection.close()

    def add_item(self, item_type, english, chinese, pronunciation="", example_en="", example_zh="", audio_path=""):
        """添加学习内容"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO learning_items 
                (type, english, chinese, pronunciation, example_en, example_zh, audio_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (item_type, english, chinese, pronunciation,
                                   example_en, example_zh, audio_path))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"添加内容出错: {e}")
            return False
        finally:
            connection.close()

    def get_items_for_learning(self, limit=50, item_type='all'):
        """获取学习内容列表"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)

            if item_type == 'all':
                query = """
                    SELECT li.* FROM learning_items li
                    LEFT JOIN learning_records lr ON li.id = lr.item_id 
                        AND lr.learned_date = CURDATE()
                    WHERE lr.id IS NULL
                    ORDER BY li.created_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
            else:
                query = """
                    SELECT li.* FROM learning_items li
                    LEFT JOIN learning_records lr ON li.id = lr.item_id 
                        AND lr.learned_date = CURDATE()
                    WHERE lr.id IS NULL AND li.type = %s
                    ORDER BY li.created_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (item_type, limit))

            items = cursor.fetchall()
            cursor.close()
            return items
        except Error as e:
            print(f"获取学习内容出错: {e}")
            return []
        finally:
            connection.close()

    def get_items_for_test(self, limit=20):
        """获取测试内容列表"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)

            # 优先获取复习内容，然后随机获取其他内容
            query = """
                (SELECT li.* FROM learning_items li
                INNER JOIN review_items ri ON li.id = ri.item_id
                WHERE ri.reviewed = FALSE
                ORDER BY ri.added_date ASC
                LIMIT %s)
                UNION
                (SELECT li.* FROM learning_items li
                WHERE li.id NOT IN (SELECT item_id FROM review_items WHERE reviewed = FALSE)
                ORDER BY RAND()
                LIMIT %s)
                LIMIT %s
            """
            cursor.execute(query, (limit // 2, limit // 2, limit))
            items = cursor.fetchall()
            cursor.close()
            return items
        except Error as e:
            print(f"获取测试内容出错: {e}")
            return []
        finally:
            connection.close()

    def add_to_review(self, items):
        """添加到复习库"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            for item in items:
                item_id = item.get('id')
                if item_id:
                    # 检查是否已存在
                    cursor.execute(
                        "SELECT id FROM review_items WHERE item_id = %s AND reviewed = FALSE",
                        (item_id,)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO review_items (item_id) VALUES (%s)",
                            (item_id,)
                        )
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"添加到复习库出错: {e}")
            return False
        finally:
            connection.close()

    def get_review_items(self, limit=50):
        """获取复习列表"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT li.*, ri.added_date
                FROM learning_items li
                INNER JOIN review_items ri ON li.id = ri.item_id
                WHERE ri.reviewed = FALSE
                ORDER BY ri.added_date ASC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            items = cursor.fetchall()
            cursor.close()
            return items
        except Error as e:
            print(f"获取复习列表出错: {e}")
            return []
        finally:
            connection.close()

    def mark_as_reviewed(self, item_id):
        """标记为已复习"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            query = """
                UPDATE review_items 
                SET reviewed = TRUE, reviewed_date = CURRENT_TIMESTAMP
                WHERE item_id = %s AND reviewed = FALSE
            """
            cursor.execute(query, (item_id,))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"标记已复习出错: {e}")
            return False
        finally:
            connection.close()

    def record_learning(self, item_id, is_correct):
        """记录学习"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            correct = 1 if is_correct else 0
            wrong = 0 if is_correct else 1

            query = """
                INSERT INTO learning_records 
                (item_id, learned_date, review_count, correct_count, wrong_count)
                VALUES (%s, CURDATE(), 1, %s, %s)
                ON DUPLICATE KEY UPDATE
                review_count = review_count + 1,
                correct_count = correct_count + %s,
                wrong_count = wrong_count + %s,
                last_review = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (item_id, correct, wrong, correct, wrong))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"记录学习出错: {e}")
            return False
        finally:
            connection.close()

    def get_statistics(self):
        """获取统计信息"""
        connection = self.get_connection()
        if not connection:
            return {
                'word_count': 0,
                'phrase_count': 0,
                'sentence_count': 0,
                'today_learned': 0
            }

        try:
            cursor = connection.cursor(dictionary=True)

            # 单词数
            cursor.execute(
                "SELECT COUNT(*) as count FROM learning_items WHERE type='word'")
            word_count = cursor.fetchone()['count']

            # 短语数
            cursor.execute(
                "SELECT COUNT(*) as count FROM learning_items WHERE type='phrase'")
            phrase_count = cursor.fetchone()['count']

            # 句子数
            cursor.execute(
                "SELECT COUNT(*) as count FROM learning_items WHERE type='sentence'")
            sentence_count = cursor.fetchone()['count']

            # 今日学习数
            cursor.execute("""
                SELECT COUNT(DISTINCT item_id) as today 
                FROM learning_records 
                WHERE learned_date = CURDATE()
            """)
            today_learned = cursor.fetchone()['today']

            cursor.close()
            return {
                'word_count': word_count,
                'phrase_count': phrase_count,
                'sentence_count': sentence_count,
                'today_learned': today_learned
            }
        except Error as e:
            print(f"获取统计信息出错: {e}")
            return {
                'word_count': 0,
                'phrase_count': 0,
                'sentence_count': 0,
                'today_learned': 0
            }
        finally:
            connection.close()

    def get_detailed_statistics(self):
        """获取详细统计"""
        connection = self.get_connection()
        if not connection:
            return {}

        try:
            cursor = connection.cursor(dictionary=True)

            # 总学习次数
            cursor.execute(
                "SELECT SUM(review_count) as total FROM learning_records")
            total_reviews = cursor.fetchone()['total'] or 0

            # 总正确次数
            cursor.execute(
                "SELECT SUM(correct_count) as total FROM learning_records")
            total_correct = cursor.fetchone()['total'] or 0

            # 总错误次数
            cursor.execute(
                "SELECT SUM(wrong_count) as total FROM learning_records")
            total_wrong = cursor.fetchone()['total'] or 0

            # 待复习数量
            cursor.execute(
                "SELECT COUNT(*) as count FROM review_items WHERE reviewed = FALSE")
            review_pending = cursor.fetchone()['count']

            cursor.close()

            accuracy = 0
            if total_correct + total_wrong > 0:
                accuracy = round(
                    (total_correct / (total_correct + total_wrong)) * 100, 2)

            return {
                'total_reviews': total_reviews,
                'total_correct': total_correct,
                'total_wrong': total_wrong,
                'review_pending': review_pending,
                'accuracy': accuracy
            }
        except Error as e:
            print(f"获取详细统计出错: {e}")
            return {}
        finally:
            connection.close()

    def get_learning_history(self, days=7):
        """获取学习历史"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    learned_date,
                    COUNT(DISTINCT item_id) as items_count,
                    SUM(review_count) as total_reviews,
                    SUM(correct_count) as correct_count,
                    SUM(wrong_count) as wrong_count
                FROM learning_records
                WHERE learned_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY learned_date
                ORDER BY learned_date DESC
            """
            cursor.execute(query, (days,))
            history = cursor.fetchall()
            cursor.close()

            # 转换日期格式
            for record in history:
                record['learned_date'] = record['learned_date'].strftime(
                    '%Y-%m-%d')

            return history
        except Error as e:
            print(f"获取学习历史出错: {e}")
            return []
        finally:
            connection.close()

    def get_today_progress(self):
        """获取今日进度"""
        connection = self.get_connection()
        if not connection:
            return {}

        try:
            cursor = connection.cursor(dictionary=True)

            # 今日学习的不同内容数
            cursor.execute("""
                SELECT COUNT(DISTINCT item_id) as count
                FROM learning_records
                WHERE learned_date = CURDATE()
            """)
            learned_count = cursor.fetchone()['count']

            # 今日复习次数
            cursor.execute("""
                SELECT SUM(review_count) as count
                FROM learning_records
                WHERE learned_date = CURDATE()
            """)
            review_count = cursor.fetchone()['count'] or 0

            # 今日正确率
            cursor.execute("""
                SELECT 
                    SUM(correct_count) as correct,
                    SUM(wrong_count) as wrong
                FROM learning_records
                WHERE learned_date = CURDATE()
            """)
            result = cursor.fetchone()
            correct = result['correct'] or 0
            wrong = result['wrong'] or 0

            accuracy = 0
            if correct + wrong > 0:
                accuracy = round((correct / (correct + wrong)) * 100, 2)

            cursor.close()

            return {
                'learned_count': learned_count,
                'review_count': review_count,
                'correct_count': correct,
                'wrong_count': wrong,
                'accuracy': accuracy
            }
        except Error as e:
            print(f"获取今日进度出错: {e}")
            return {}
        finally:
            connection.close()

    def get_learning_streak(self):
        """获取连续学习天数"""
        connection = self.get_connection()
        if not connection:
            return 0

        try:
            cursor = connection.cursor(dictionary=True)

            # 获取所有学习日期（倒序）
            cursor.execute("""
                SELECT DISTINCT learned_date
                FROM learning_records
                ORDER BY learned_date DESC
            """)
            dates = cursor.fetchall()
            cursor.close()

            if not dates:
                return 0

            # 计算连续天数
            streak = 0
            today = date.today()

            for i, record in enumerate(dates):
                expected_date = today - timedelta(days=i)
                if record['learned_date'] == expected_date:
                    streak += 1
                else:
                    break

            return streak
        except Error as e:
            print(f"获取连续学习天数出错: {e}")
            return 0
        finally:
            connection.close()


    # 用户相关方法
    def create_user(self, username, email, password):
        """创建用户"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor()
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Error as e:
            print(f"创建用户失败: {e}")
            return None
        finally:
            connection.close()


    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"获取用户失败: {e}")
            return None
        finally:
            connection.close()


    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"获取用户失败: {e}")
            return None
        finally:
            connection.close()


    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"获取用户失败: {e}")
            return None
        finally:
            connection.close()


    def update_user_token(self, user_id, token):
        """更新用户token"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            query = "UPDATE users SET token = %s, last_login = CURRENT_TIMESTAMP WHERE id = %s"
            cursor.execute(query, (token, user_id))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"更新token失败: {e}")
            return False
        finally:
            connection.close()


    def clear_user_token(self, user_id):
        """清除用户token"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            query = "UPDATE users SET token = NULL WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"清除token失败: {e}")
            return False
        finally:
            connection.close()


    def update_user_profile(self, user_id, email=None, avatar=None):
        """更新用户资料"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            updates = []
            params = []

            if email:
                updates.append("email = %s")
                params.append(email)
            if avatar:
                updates.append("avatar = %s")
                params.append(avatar)

            if not updates:
                return True

            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"更新资料失败: {e}")
            return False
        finally:
            connection.close()


    def update_user_password(self, user_id, new_password):
        """更新用户密码"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            query = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(query, (new_password, user_id))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"更新密码失败: {e}")
            return False
        finally:
            connection.close()




    def close(self):
        """关闭连接池"""
        # 连接池会自动管理连接
        pass
